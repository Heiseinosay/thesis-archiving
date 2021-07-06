from flask import Blueprint, render_template, request, send_file
from flask_login import login_required

from sqlalchemy import or_

from thesis_archiving.models import Log, User
from thesis_archiving.utils import export_to_excel, has_roles

log = Blueprint("log", __name__, url_prefix="/log")

@log.route("/read")
@login_required
@has_roles("is_admin")
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

@log.route("/export")
@login_required
@has_roles("is_admin")
def export():

    data = [
        [
            log.date.isoformat(),
            log.user.username,
            log.user.full_name,
            log.description
        ] for log in Log.query.order_by(Log.date.desc()).all()
    ]

    columns = [
        "date",
        "username",
        "full_name",
        "description"
    ]

    output, download_name = export_to_excel('thesis-archiving-log-', data, columns)

    return send_file(output, as_attachment=True, download_name=download_name)