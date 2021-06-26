from flask import Blueprint, url_for, redirect, render_template, request, flash, send_file
from flask_login import login_user, current_user, login_required, logout_user
from thesis_archiving import bcrypt, db
from thesis_archiving.user.validation import LoginSchema, validate_input
from thesis_archiving.models import User, Log
from thesis_archiving.utils import export_to_excel
from sqlalchemy import or_

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

@user.route("/read")
@login_required
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