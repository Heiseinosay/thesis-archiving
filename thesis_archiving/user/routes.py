from flask import Blueprint, url_for, redirect, render_template, request, flash, send_file
from sqlalchemy.sql.expression import false
from flask_login import login_user, current_user, login_required, logout_user

from sqlalchemy import or_

from thesis_archiving import bcrypt, db
from thesis_archiving.utils import export_to_excel, has_roles
from thesis_archiving.models import User, Log
from thesis_archiving.validation import validate_input

from thesis_archiving.user.validation import LoginSchema, CreateUserSchema, UpdateUserSchema, PasswordResetSchema, PasswordResetRequestSchema
from thesis_archiving.user.utils import send_reset_request

# from pprint import pprint

user = Blueprint('user', __name__, url_prefix="/user")

@user.route("/login", methods=["POST","GET"])
def login():
    if current_user.is_authenticated:
        return redirect(url_for("thesis.read"))
        
    result = {
        'valid' : {},
        'invalid' : {}
    }
    
    if request.method == "POST":

        # contains form data converted to mutable dict
        data = request.form.to_dict()
        
        # marshmallow validation
        result = validate_input(data, LoginSchema)
        
        if not result['invalid']:
            user = User.query.filter_by(username=data["username"]).first()
            
            if user and bcrypt.check_password_hash(user.password, data["password"]):
                login_user(user)
                
                # wag na ilagay sa desc ang name para dynamic. mag refer nalang sa FK/backref obj
                log = Log(description=f"Logged in.")
                log.user = current_user

                try:
                    db.session.add(log)
                    db.session.commit()
                except:
                    flash("An error occured while trying to log.","danger")

                next_page = request.args.get('next')
                return redirect(next_page) if next_page else redirect(url_for("thesis.read"))

            else:
                result["valid"] = {}
                flash("Login credentials are invalid or do not match.","danger")

    return render_template("user/login.html", result = result)

@user.route("/logout")
@login_required
def logout():
    log = Log(description=f"Logged out.")
    log.user = current_user

    try:
        db.session.add(log)
        db.session.commit()
    except:
        flash("An error occured while trying to log.","danger")

    logout_user()
    
    return redirect(url_for("user.login"))

@user.route("/password/reset/<token>", methods=["POST", "GET"])
def password_reset(token):
    
    if current_user.is_authenticated:
        return redirect(url_for("main.home"))

    _user = User.verify_reset_token(token)

    if _user is None:
        flash('Token is invalid or expired.','danger')
        return redirect(url_for('user.login'))

    result = {
        'valid' : {},
        'invalid' : {}
    }

    if request.method == "POST":
        # contains form data converted to mutable dict
        data = request.form.to_dict()
        
        # marshmallow validation
        result = validate_input(data, PasswordResetSchema)

        if not result['invalid']:
            _user.password = bcrypt.generate_password_hash(data['password']).decode("utf-8")
            
            try:
                db.session.commit()
                flash("Password successfully changed.","success")
                return redirect(url_for('user.login'))
            except:
                flash("An error occured.","danger")

    return render_template("user/password/reset.html", result=result)

@user.route("/password/reset_request", methods=["POST", "GET"])
def password_reset_request():

    if current_user.is_authenticated:
        return redirect(url_for("main.home"))

    result = {
        'valid' : {},
        'invalid' : {}
    }

    if request.method == "POST":
        # contains form data converted to mutable dict
        data = request.form.to_dict()
        
        # marshmallow validation
        result = validate_input(data, PasswordResetRequestSchema)

        if not result['invalid']:
            _user = User.query.filter_by(email=data['email']).first()
            
            send_reset_request(_user)
            
            flash("Reset request sent (expires in 3 days). Please check your inbox or spam folder. This may take some time.","success")
            
            return redirect(url_for("user.login"))

    return render_template("user/password/reset_request.html", result=result)

@user.route("/read")
@login_required
@has_roles("is_admin")
def read():
    # login 
    page = request.args.get('page', 1, type=int)
    search = '%' + request.args.get('search', '') + '%'
    
    users = User.query.filter(
            or_(
                User.username.like(search),
                User.full_name.like(search)
            )
        ).order_by(User.full_name).paginate(error_out=False)

    return render_template("user/read.html", users=users)

@user.route("/export")
@login_required
@has_roles("is_admin")
def export():
    
    data = [ 
        [
            user.username,
            user.full_name,
            user.email,
            user.is_adviser,
            user.is_admin,
            user.is_superuser
        ] for user in User.query.order_by(User.full_name).all()
    ] 
    
    columns = [
        "username",
        "full_name",
        "email",
        "is_adviser",
        "is_admin",
        "is_superuser"
    ]

    output, download_name = export_to_excel('thesis-archiving-user-', data, columns)

    return send_file(output, as_attachment=True, download_name=download_name)

@user.route("/create", methods=["POST","GET"])
@login_required
@has_roles("is_superuser")
def create():
    result = {
        'valid' : {},
        'invalid' : {}
    }

    if request.method == "POST":
        
        # contains form data converted to mutable dict
        data = request.form.to_dict()
        
        
        # marshmallow validation
        result = validate_input(data, CreateUserSchema)

        if not result['invalid']:
            # prevent premature flushing
            with db.session.no_autoflush:
                # values for validated and filtered input
                data = result['valid']
                
                # init model obj + fill in values
                _user = User()

                _user.username = data['username']
                _user.full_name = data['full_name']
                _user.email = data['email']
                _user.password = bcrypt.generate_password_hash(data['password']).decode("utf-8")
                _user.is_adviser = data['is_adviser']
                _user.is_admin = data['is_admin']
                _user.is_superuser = data['is_superuser']

                try:
                    db.session.add(_user)
                    db.session.commit()
                    flash("Successfully created new user.", "success")
                    return redirect(url_for('user.read'))

                except:
                    flash("An error occured", "danger")

    return render_template("user/create.html", result=result)

@user.route("/update/<int:user_id>", methods=["POST", "GET"])
@login_required
@has_roles("is_admin")
def update(user_id):

    _user = User.query.get_or_404(user_id)

    result = {
        'valid' : {},
        'invalid' : {}
    }

    if request.method == "POST":
        # contains form data converted to mutable dict
        data = request.form.to_dict()
        
        
        # marshmallow validation
        result = validate_input(data, UpdateUserSchema, user_obj=_user)

        if not result['invalid']:
            # prevent premature flushing
            with db.session.no_autoflush:
                # values for validated and filtered input
                data = result['valid']

                _user.username = data['username']
                _user.full_name = data['full_name']
                _user.email = data['email']
                _user.is_adviser = data['is_adviser']
                _user.is_admin = data['is_admin']
                _user.is_superuser = data['is_superuser']

                try:
                    db.session.commit()
                    flash("Successfully updated user.", "success")
                    return redirect(request.referrer)

                except:
                    flash("An error occured", "danger")

    return render_template("user/update.html", result=result, user=_user)

@user.route("/delete/<int:user_id>", methods=["POST"])
@login_required
@has_roles("is_superuser")
def delete(user_id):
    _user = User.query.get_or_404(user_id)
    
    try:
        db.session.delete(_user)
        db.session.commit()
        flash("Successfully deleted a user.","success")
        
        return redirect(request.referrer)
    except:
        flash("An error occured.","danger")

    return redirect(url_for('user.read'))