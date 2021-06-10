from flask import Blueprint, url_for, redirect, render_template, request
from thesis_archiving.user.validation import LoginSchema, validate_input
# from pprint import pprint


user = Blueprint('user', __name__, url_prefix="/user")

@user.route("/login", methods=["POST","GET"])
def login():

    valid = {}
    invalid = {}

    if request.method == "POST":
        valid, invalid = validate_input(request.form, LoginSchema)
        
        if not invalid:
            return redirect(url_for("thesis.read"))

    return render_template("user/login.html", valid=valid, invalid=invalid)

@user.route("/read")
def read():
    # login req
    return "list of user"
