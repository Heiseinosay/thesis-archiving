from flask import Blueprint, url_for, redirect, render_template, request, flash
from flask_login import login_user, current_user, login_required, logout_user
from thesis_archiving import bcrypt, db
from thesis_archiving.user.validation import LoginSchema, validate_input
from thesis_archiving.models import User, Log
from sqlalchemy import or_
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
