from flask import Blueprint, render_template, request
from flask_login import login_required
from thesis_archiving.models import Thesis

thesis = Blueprint("thesis", __name__, url_prefix="/thesis")

# wrap whole blueprint to be login required
@thesis.before_request
@login_required

@thesis.route("/read")
def read():
    # login req
    page = request.args.get('page', 1, type=int)
    theses = Thesis.query.order_by(Thesis.date_registered.desc()).order_by(Thesis.id.desc()).order_by(Thesis.number.desc()).paginate(page=page, per_page=25)

    return render_template("thesis/read.html", theses=theses)
