from types import resolve_bases
from flask import Blueprint, url_for, redirect, render_template, request
from thesis_archiving.user.validation import LoginSchema, validate_input
from pprint import pprint


user = Blueprint('user', __name__, url_prefix="/user")

@user.route("/login", methods=["POST","GET"])
def login():

    result = {}

    if request.method == "POST":
        result = validate_input(request.form, LoginSchema)
        
        if not result['invalid']:
            return redirect(url_for("thesis.read"))

    return render_template("user/login.html", result = result)

@user.route("/read")
def read():
    # login req
    return "list of user"
