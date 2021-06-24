from flask import Blueprint, render_template, request
from flask_login import login_required
from thesis_archiving.models import Program

program = Blueprint("program", __name__, url_prefix="/program")

@program.before_request
@login_required

@program.route("/read")
def read():
    page = request.args.get('page', 1, type=int)
    programs = Program.query.order_by(Program.name).paginate()

    return render_template("program/read.html", programs=programs)

