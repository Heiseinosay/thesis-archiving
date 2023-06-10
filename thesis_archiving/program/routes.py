from flask import Blueprint, render_template, request, flash, url_for, redirect
from flask_login import login_required

from sqlalchemy import or_

from thesis_archiving import db
from thesis_archiving.models import Program
from thesis_archiving.utils import has_roles

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

@program.route("/delete/<int:program_id>", methods=["POST"])
@login_required
@has_roles("is_superuser")
def delete(program_id):
    _program = Program.query.get_or_404(program_id)
    
    try:
        db.session.delete(_program)
        db.session.commit()
        flash("Successfully deleted a program.","success")
        
        return redirect(request.referrer)
    except:
        flash("An error occured.","danger")

    return redirect(url_for('program.read'))