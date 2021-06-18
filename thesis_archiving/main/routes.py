from flask import Blueprint, url_for, redirect, render_template
from flask_login import login_required

main = Blueprint('main', __name__)

@main.before_request
@login_required

@main.route("/")
@login_required
def home():
    # redir to login if anon
    # redir to thesis read if logged in
    return redirect(url_for("thesis.read"))