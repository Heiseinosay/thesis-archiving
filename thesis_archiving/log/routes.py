from flask import Blueprint, render_template, request
from flask_login import login_required
from thesis_archiving.models import Log, User
from sqlalchemy import or_

log = Blueprint("log", __name__, url_prefix="/log")

@log.before_request
@login_required

@log.route("/read")
def read():
    page = request.args.get('page', 1, type=int)
    search = '%' + request.args.get('search', '') + '%'

    # if search is not empty, query username and first name matches for Log
    if search[1] != '%':
        users = [u.id for u in User.query.filter(or_(User.username.like(search), User.full_name.like(search))).all()]
        logs = Log.query.filter(Log.user_id.in_(users)).order_by(Log.date.desc()).paginate()
    else:
        logs = Log.query.order_by(Log.date.desc()).paginate()

    return render_template("log/read.html", logs=logs)