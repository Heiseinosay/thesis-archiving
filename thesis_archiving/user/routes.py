from flask import Blueprint, url_for, redirect, render_template

user = Blueprint('user', __name__, url_prefix="/user")

@user.route("/login")
def login():
    return render_template("user/login.html")

@user.route("/read")
def read():
    # login req
    return "list of user"
