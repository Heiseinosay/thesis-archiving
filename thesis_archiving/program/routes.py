from flask import Blueprint, render_template, request
from flask_login import login_required
from thesis_archiving.models import Program
from thesis_archiving.utils import has_roles
from sqlalchemy import or_

program = Blueprint("program", __name__, url_prefix="/program")

@program.route("/read")
@login_required
@has_roles("is_admin")
def read():
    page = request.args.get('page', 1, type=int)
    search = '%' + request.args.get('search', '') + '%'

    programs = Program.query.filter(
            or_(
                Program.name.like(search),
                Program.code.like(search)
            )
        ).order_by(Program.name).paginate(error_out=False)

    return render_template("program/read.html", programs=programs)

