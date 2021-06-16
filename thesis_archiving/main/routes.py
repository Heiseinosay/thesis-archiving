from flask import Blueprint, url_for, redirect, render_template

main = Blueprint('main', __name__)

@main.route("/")
def home():
    # redir to login if anon
    # redir to thesis read if logged in
    return redirect(url_for("thesis.read"))

@main.route("/test")
def test():
    return render_template("components/base.html")