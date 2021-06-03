from flask import Blueprint, url_for, redirect

main = Blueprint('main', __name__)

@main.route("/")
def home():
    # redir to login if anon
    # redir to thesis read if logged in
    return redirect(url_for("thesis.read"))
