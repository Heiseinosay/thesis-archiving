from flask import Blueprint, render_template, request, flash, url_for, redirect
from flask_login import login_required

from sqlalchemy import or_

from thesis_archiving import db
from thesis_archiving.models import Program
from thesis_archiving.utils import has_roles
from thesis_archiving.validation import validate_input

from thesis_archiving.program.validation import CreateProgramSchema

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

@program.route("/create", methods=["POST","GET"])
@login_required
@has_roles("is_superuser")
def create():
    result = {
        'valid' : {},
        'invalid' : {}
    }

    if request.method == "POST":
        
        # contains form data converted to mutable dict
        data = request.form.to_dict()
        
        # marshmallow validation
        result = validate_input(data, CreateProgramSchema)

        if not result['invalid']:
            # prevent premature flushing
            with db.session.no_autoflush:
                # values for validated and filtered input
                data = result['valid']
                
                # init model obj + fill in values
                _program = Program()

                _program.name = data['name']
                _program.code = data['code']

                try:
                    db.session.add(_program)
                    db.session.commit()
                    flash("Successfully created new program.", "success")
                    return redirect(url_for('program.read'))

                except:
                    flash("An error occured", "danger")

    return render_template("program/create.html", result=result)

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