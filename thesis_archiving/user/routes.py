from flask import Blueprint, url_for, redirect

user = Blueprint('user', __name__, url_prefix="/user")

@user.route("/read")
def read():
    # login req
    return "list of user"
