from flask import Blueprint, url_for, redirect, render_template, request, flash
from flask_login import login_user, current_user, login_required
from thesis_archiving import bcrypt
from thesis_archiving.user.validation import LoginSchema, validate_input
from thesis_archiving.models import User
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
                return redirect(url_for("thesis.read")) # arg next
            else:
                result["valid"] = {}
                flash("Login credentials are invalid or do not match.","danger")

    return render_template("user/login.html", result = result)

@user.route("/read")
@login_required
def read():
    # login req
    return "list of user"
