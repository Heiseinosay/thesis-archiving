from flask import Blueprint, url_for, redirect, render_template
from flask_login import current_user

main = Blueprint('main', __name__)

@main.route("/")
def home():
    # redir to thesis read if logged in
    if current_user.is_authenticated:
        return redirect(url_for("thesis.read"))
    
    # redir to login if anon
    return redirect(url_for("user.login"))