from flask import Blueprint, render_template, request, redirect, url_for, send_file, flash
from flask_login import login_required
from thesis_archiving import db
from thesis_archiving.models import Thesis, User, Program, Category
from thesis_archiving.utils import export_to_excel
from thesis_archiving.validation import validate_input
from thesis_archiving.thesis.validation import CreateThesisSchema
from sqlalchemy import or_
from datetime import datetime
import pytz
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
def create():
    result = {
        'valid' : {},
        'invalid' : {}
    }

    choices = {
        'adviser_id' : {adviser.id : adviser.full_name for adviser in User.query.filter_by(is_adviser=True).order_by(User.full_name).all()},
        'program_id' : {program.id : program.name for program in Program.query.order_by(Program.name).all()},
        'category_id' : {category.id : category.name for category in Category.query.order_by(Category.name).all()},
        'sy_start' : { year : year for year in range(2000, datetime.now(tz=pytz.timezone('Asia/Manila')).year + 1)},
        'semester' : {1:1, 2:2},
        'is_old' : {1:'Old', 0:'New'}
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

    return render_template("thesis/create.html", result=result, choices=choices)