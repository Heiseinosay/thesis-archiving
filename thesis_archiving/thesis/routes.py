from flask import Blueprint, render_template, request, redirect, url_for, send_file, flash
from flask_login import login_required
from thesis_archiving import db
from thesis_archiving.models import Thesis, User, Program, Category
from thesis_archiving.utils import export_to_excel, has_roles
from thesis_archiving.validation import validate_input
from thesis_archiving.thesis.validation import CreateThesisSchema, UpdateThesisSchema
from thesis_archiving.thesis.utils import select_choices
from sqlalchemy import or_
from pprint import pprint

thesis = Blueprint("thesis", __name__, url_prefix="/thesis")

@thesis.route("/read")
@login_required
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
            )

    # refine query by adviser and proponents if search query is not just the 2 wildcards
    if len(search) > 2:
        advisers = [a.id for a in User.query.filter_by(is_adviser=True).filter(or_(User.username.like(search), User.full_name.like(search))).all()]
        theses = theses.union_all(Thesis.query.filter(Thesis.adviser_id.in_(advisers)))
        
        # todo, proponents filtering

        # users = [u.id for u in User.query.filter_by(is_adviser=False).filter(or_(User.username.like(search), User.full_name.like(search))).all()]
        # theses = theses.union_all(Thesis.query.filter(Thesis.proponents.))

    theses = theses.order_by(Thesis.date_registered.desc()).order_by(Thesis.id.desc()).order_by(Thesis.number.desc()).paginate(page=page, per_page=25, error_out=False)

    return render_template("thesis/read.html", theses=theses)

@thesis.route("/export")
@login_required
@has_roles("is_admin")
def export():

    # rows
    data = [ 
        [
            thesis.title,
            thesis.is_old,

            thesis.sy_start,
            thesis.semester,
            thesis.category.name,
            thesis.program.name,
            thesis.number,
            
            thesis.adviser.full_name,
            (''.join([user.username + ',' for user in thesis.proponents]))[:-1] if thesis.proponents.count() > 0 else None,

            thesis.area,
            thesis.keywords,
            thesis.date_deployed,

            thesis.overview
            
        ] for thesis in Thesis.query.order_by(Thesis.is_old, Thesis.title).all()
    ] 
    
    # headers
    columns = [
        "title",
        "is_old",
        "sy_start",
        "semester",
        "category",
        "program",
        "number",
        "adviser",
        "proponents",
        "area",
        "keywords",
        "date_deployed",
        "overview"
    ]

    output, download_name = export_to_excel("thesis-archiving-thesis-", data, columns)

    return send_file(output, as_attachment=True, download_name=download_name)

@thesis.route("/create", methods=["POST", "GET"])
@login_required
@has_roles("is_admin")
def create():
    result = {
        'valid' : {},
        'invalid' : {}
    }

    if request.method == "POST":

        # contains form data converted to mutable dict
        data = request.form.to_dict()
        
        # marshmallow validation
        result = validate_input(data, CreateThesisSchema)
        
        if not result['invalid']:
            # prevent premature flushing
            with db.session.no_autoflush:
                # values for validated and filtered input
                data = result['valid']
                
                # init model obj + fill in values
                _thesis = Thesis()

                _thesis.title = data['title']
                _thesis.sy_start = data['sy_start']
                _thesis.semester = data['semester']
                _thesis.is_old = data['is_old']
                _thesis.area = data['area']
                _thesis.keywords = data['keywords']
                _thesis.overview = data['overview']

                _thesis.adviser = User.query.get(data['adviser_id'])
                _thesis.program = Program.query.get(data['program_id'])
                _thesis.category = Category.query.get(data['category_id'])
                
                if not _thesis.is_old:
                    _thesis.number = Thesis.thesis_number()
                
                for p in data['proponents']:
                    _thesis.proponents.append(User.query.filter_by(username=p).first())

                try:
                    db.session.add(_thesis)
                    db.session.commit()
                    flash("Successfully created new thesis.", "success")
                    return redirect(url_for('thesis.read'))

                except:
                    flash("An error occured", "danger")

    return render_template("thesis/create.html", result=result, select_choices=select_choices())

@thesis.route("/update/<int:thesis_id>", methods=["POST", "GET"])
@login_required
@has_roles("is_admin")
def update(thesis_id):
    _thesis = Thesis.query.get_or_404(thesis_id)

    result = {
        'valid' : {},
        'invalid' : {}
    }

    if request.method == "POST":
        # contains form data converted to mutable dict
        data = request.form.to_dict()
        
        # marshmallow validation
        result = validate_input(data, UpdateThesisSchema)
        
        if not result['invalid']:
            # prevent premature flushing
            with db.session.no_autoflush:
                # values for validated and filtered input
                data = result['valid']

                _thesis.title = data['title']
                _thesis.sy_start = data['sy_start']
                _thesis.semester = data['semester']
                _thesis.is_old = data['is_old']
                _thesis.area = data['area']
                _thesis.keywords = data['keywords']
                _thesis.overview = data['overview']

                _thesis.adviser = User.query.get(data['adviser_id'])
                _thesis.program = Program.query.get(data['program_id'])
                _thesis.category = Category.query.get(data['category_id'])
                
                # when setting to new batch, add number
                if not _thesis.is_old and not _thesis.number:
                    _thesis.number = Thesis.thesis_number()

                try:
                    db.session.commit()
                    flash("Successfully updated thesis.", "success")
                    return redirect(request.referrer)

                except:
                    flash("An error occured", "danger")

    return render_template("thesis/update.html", thesis=_thesis, result=result, select_choices=select_choices())

@thesis.route("/delete/<int:thesis_id>", methods=["POST"])
@login_required
@has_roles("is_admin")
def delete(thesis_id):
    _thesis = Thesis.query.get_or_404(thesis_id)
    print(_thesis)
    try:
        db.session.delete(_thesis)
        db.session.commit()
        flash("Successfully deleted a thesis.","success")
        return redirect(request.referrer)
    except:
        flash("An error occured.","danger")

    return redirect(url_for('thesis.read'))

@thesis.route("/proponent/add/<int:thesis_id>", methods=["POST"])
@login_required
@has_roles("is_admin")
def proponent_add(thesis_id):

    _thesis = Thesis.query.get_or_404(thesis_id)
    _user = User.query.filter_by(username=request.form['username']).first()

    if _user:
        if _user in _thesis.proponents:
            flash("User is already a proponent.", "warning")
        else:
            try:
                _thesis.proponents.append(_user)
                db.session.commit()
                flash("Proponent successfully added.", "success")    
            except:
                flash("An error occured.", "danger")    
    else:
        flash("User does not exist.", "danger")


    return redirect(url_for("thesis.update", thesis_id=_thesis.id))

@thesis.route("/proponent/remove/<int:thesis_id>/<int:user_id>", methods=["POST"])
@login_required
@has_roles("is_admin")
def proponent_remove(thesis_id, user_id):
    
    _thesis = Thesis.query.get_or_404(thesis_id)
    _user = User.query.get_or_404(user_id)
    try:
        _thesis.proponents.remove(_user)
        db.session.commit()
        flash("Successfully removed a proponent", "success")
    except:
        flash("An error occured.", "danger")

    return redirect(url_for("thesis.update", thesis_id=_thesis.id))