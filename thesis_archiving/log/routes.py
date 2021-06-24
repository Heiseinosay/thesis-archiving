from flask import Blueprint, render_template, request
from flask_login import login_required
from thesis_archiving.models import Log

log = Blueprint("log", __name__, url_prefix="/log")

@log.before_request
@login_required

@log.route("/read")
def read():
    page = request.args.get('page', 1, type=int)
    logs = Log.query.order_by(Log.date.desc()).paginate()

    return render_template("log/read.html", logs=logs)