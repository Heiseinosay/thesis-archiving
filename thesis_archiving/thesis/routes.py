from flask import Blueprint, render_template, request
from flask_login import login_required
from thesis_archiving.models import Thesis
from sqlalchemy import or_

thesis = Blueprint("thesis", __name__, url_prefix="/thesis")

# wrap whole blueprint to be login required
@thesis.before_request
@login_required

@thesis.route("/read")
def read():
    # login req
    page = request.args.get('page', 1, type=int)
    search = '%' + request.args.get('search', '') + '%'

    theses = Thesis.query.filter(
            or_(
                Thesis.title.like(search),
                Thesis.area.like(search),
                Thesis.keywords.like(search)
            )
        ).order_by(Thesis.date_registered.desc()).order_by(Thesis.id.desc()).order_by(Thesis.number.desc()).paginate(page=page, per_page=25, error_out=False)
    print(dir(Thesis.adviser))
    return render_template("thesis/read.html", theses=theses)
