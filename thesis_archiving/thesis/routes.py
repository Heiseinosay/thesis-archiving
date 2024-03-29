from flask import Blueprint, render_template, request, redirect, url_for, send_from_directory, flash, abort, current_app
from flask.helpers import send_file
from flask_login import login_required, current_user
import time

from sqlalchemy import or_, and_

from thesis_archiving import db
from thesis_archiving.models import QuantitativeCriteria, QuantitativePanelistGrade, QuantitativeRating, Thesis, User, Program, Category, Group, QuantitativeCriteriaGrade
from thesis_archiving.utils import export_to_excel, has_roles
from thesis_archiving.validation import validate_input

from thesis_archiving.thesis.validation import CreateThesisSchema, UpdateThesisSchema
from thesis_archiving.thesis.utils import select_choices, proposal_form_name, save_proposal_form, remove_proposal_form

from pprint import pprint
from datetime import datetime
import pytz, os

thesis = Blueprint("thesis", __name__, url_prefix="/thesis")

@thesis.route("/read")
@login_required
def read():
    
    # url params
    page = request.args.get('page', 1, type=int)
    search = '%' + request.args.get('search', '') + '%'
    program_id = request.args.get('program_id', type=int)
    category_id = request.args.get('category_id', type=int)
    sy_start = request.args.get('sy_start', type=int)
    
    # base query
    theses = Thesis.query

    # general search
    theses = theses.filter(
                or_(
                    Thesis.title.like(search),
                    Thesis.area.like(search),
                    Thesis.keywords.like(search),
                    Thesis.overview.like(search)
                )
            )
    
    # refine by program
    if program_id:
        theses = theses.filter_by(program_id=program_id)
    
    # refine by category
    if category_id:
        theses = theses.filter_by(category_id=category_id)

    # refine by school year started
    if sy_start:
        theses = theses.filter_by(sy_start=sy_start)

    # refine query by adviser and proponents if search query is not just the 2 wildcards
    if len(search) > 2:
        advisers = [a.id for a in User.query.filter_by(is_adviser=True).filter(or_(User.username.like(search), User.full_name.like(search))).all()]
        theses = theses.union_all(Thesis.query.filter(Thesis.adviser_id.in_(advisers)))
        
        # todo, proponents filtering

        # users = [u.id for u in User.query.filter_by(is_adviser=False).filter(or_(User.username.like(search), User.full_name.like(search))).all()]
        # theses = theses.union_all(Thesis.query.filter(Thesis.proponents.))

    # limit results for students
    if current_user.is_student:
        category_ = [
                        categ.id for categ in Category.query.filter(
                            or_(
                                Category.name.like("Approved Title - On Going"),
                                Category.name.like("Completed Title")
                                )
                            ).all()
                    ]
        
        theses = theses.filter(
                    Thesis.category_id.in_(category_)
                )

    # paginate resulting query
    theses = theses.order_by(Thesis.date_registered.desc()).order_by(Thesis.id.desc()).order_by(Thesis.number.desc()).paginate(page=page, per_page=25, error_out=False)

    # select choices
    programs = Program.query.order_by(Program.name).all()
    categories = Category.query.order_by(Category.name).all()
    years = [ year for year in range(2000, datetime.now(tz=pytz.timezone('Asia/Manila')).year + 1) ]

    return render_template("thesis/read.html", theses=theses, programs=programs, categories=categories, years=years)

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
        data.update(request.files)

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

                # when assigned a group
                if data.get('group_id'):
                    group_ = Group.query.get(data['group_id'])
                    _thesis.group = group_

                
                # when assigned new manuscript rating,
                if data.get('quantitative_rating_id'):

                    # id of new rating
                    id = data['quantitative_rating_id']
                    
                    if id != _thesis.quantitative_rating_id:
                        
                        # https://stackoverflow.com/questions/39773560/sqlalchemy-how-do-you-delete-multiple-rows-without-querying    

                        # bulk deletes bypasses in-python cascades but not fk(ondelete='cascade')
                        # https://stackoverflow.com/questions/46904273/sqlalchemy-delete-all-items-and-not-just-the-first#comment80807412_46904371

                        # madelete lang dapat ay yung manuscript lang hindi lahat!
                        # query = QuantitativePanelistGrade.__table__.delete()\
                        #     .where(QuantitativePanelistGrade.thesis_id == _thesis.id)
                        
                        # delete its current quanti grades
                        query = QuantitativePanelistGrade.__table__.delete()\
                            .where(    
                                and_(
                                    # get the panelist grade id who graded those criteria
                                    QuantitativePanelistGrade.id.in_(
                                        db.session.query(QuantitativeCriteriaGrade.quantitative_panelist_grade_id).where(
                                            # get id of grades pointing to those criteria
                                            QuantitativeCriteriaGrade.quantitative_criteria_id.in_(
                                                # obtain all id ng MANUSCRIPT rating criteria ng thesis
                                                db.session.query(QuantitativeCriteria.id).where(QuantitativeCriteria.quantitative_rating_id == _thesis.quantitative_rating_id)        
                                            )
                                        )
                                    ),
                                    QuantitativePanelistGrade.thesis_id == _thesis.id
                                )
                            )
                        
                        # assign to new manuscript rating
                        _thesis.quantitative_rating_id = id

                        try:
                            db.session.execute(query)
                            flash("Successfully deleted current manuscript rating grades.", "success")
                        except:
                            flash("An error occured while deleting current manuscript grades.", "danger")
                else:
                    id = _thesis.quantitative_rating_id

                    # delete current manuscript rating if None is selected
                    if id:
                        query = QuantitativePanelistGrade.__table__.delete()\
                                .where(    
                                    and_(
                                        # get the panelist id who graded those criteria
                                        QuantitativePanelistGrade.id.in_(
                                            db.session.query(QuantitativeCriteriaGrade.quantitative_panelist_grade_id).where(
                                                # get id of grades pointing to those criteria
                                                QuantitativeCriteriaGrade.quantitative_criteria_id.in_(
                                                    # obtain all id ng MANUSCRIPT rating criteria ng thesis
                                                    db.session.query(QuantitativeCriteria.id).where(QuantitativeCriteria.quantitative_rating_id == id)        
                                                )
                                            )
                                        ),
                                        QuantitativePanelistGrade.thesis_id == _thesis.id
                                    )
                                )
                        
                        # set to none
                        _thesis.quantitative_rating_id = None

                        try:
                            db.session.execute(query)
                            flash("Successfully deleted current manuscript rating grades.", "success")
                        except:
                            flash("An error occured while deleting current manuscript grades.", "danger")
                    
                # when assigned new developed thesis project rating,
                if data.get('quantitative_rating_developed_id'):

                    # id of new rating
                    id = data['quantitative_rating_developed_id']
                    
                    if id != _thesis.quantitative_rating_developed_id:
                        
                        # delete its current quanti grades
                        query = QuantitativePanelistGrade.__table__.delete()\
                            .where(    
                                and_(
                                    # get the panelist grade id who graded those criteria
                                    QuantitativePanelistGrade.id.in_(
                                        db.session.query(QuantitativeCriteriaGrade.quantitative_panelist_grade_id).where(
                                            # get id of grades pointing to those criteria
                                            QuantitativeCriteriaGrade.quantitative_criteria_id.in_(
                                                # obtain all id ng developed thesis project rating criteria ng thesis
                                                db.session.query(QuantitativeCriteria.id).where(QuantitativeCriteria.quantitative_rating_id == _thesis.quantitative_rating_developed_id)        
                                            )
                                        )
                                    ),
                                    QuantitativePanelistGrade.thesis_id == _thesis.id
                                )
                            )
                        
                        # assign to new developed thesis project rating
                        _thesis.quantitative_rating_developed_id = id

                        try:
                            db.session.execute(query)
                            flash("Successfully deleted current developed thesis project rating grades.", "success")
                        except:
                            flash("An error occured while deleting current developed thesis project grades.", "danger")
                else:
                    id = _thesis.quantitative_rating_developed_id

                    # delete current developed thesis project rating if None is selected
                    if id:
                        query = QuantitativePanelistGrade.__table__.delete()\
                                .where(    
                                    and_(
                                        # get the panelist id who graded those criteria
                                        QuantitativePanelistGrade.id.in_(
                                            db.session.query(QuantitativeCriteriaGrade.quantitative_panelist_grade_id).where(
                                                # get id of grades pointing to those criteria
                                                QuantitativeCriteriaGrade.quantitative_criteria_id.in_(
                                                    # obtain all id ng developed thesis project rating criteria ng thesis
                                                    db.session.query(QuantitativeCriteria.id).where(QuantitativeCriteria.quantitative_rating_id == id)        
                                                )
                                            )
                                        ),
                                        QuantitativePanelistGrade.thesis_id == _thesis.id
                                    )
                                )
                        
                        # set to none
                        _thesis.quantitative_rating_developed_id = None

                        try:
                            db.session.execute(query)
                            flash("Successfully deleted current developed thesis project rating grades.", "success")
                        except:
                            flash("An error occured while deleting current developed thesis project grades.", "danger")

                if data.get('proposal_form'):
                    
                    file = data.get('proposal_form')
                    
                    try:
                        save_proposal_form(_thesis, file)

                    except:
                        flash("An error occured while saving file.", "danger")



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
    
    try:
        remove_proposal_form(_thesis)
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

@thesis.route("/download/proposal_form/<int:thesis_id>")
@login_required
@has_roles("is_admin")
def download_proposal_form(thesis_id):

    thesis = Thesis.query.get_or_404(thesis_id)

    path = os.path.join( 
        current_app.root_path,
        "static", 
        "thesis_attachments", 
        "proposal_form", 
        str(thesis.sy_start),
        thesis.proposal_form
        )

    if os.path.exists(path):
        # as_attachment = False to view first
        return send_file(path, attachment_filename=thesis.proposal_form, as_attachment=False, mimetype='application/pdf')
    else:
        abort(404)

@thesis.route("<int:thesis_id>/revision-list")
@login_required
@has_roles("is_adviser", "is_guest_panelist")
def ajax_revision_list(thesis_id):

    thesis_ = Thesis.query.get_or_404(thesis_id)
    revision = thesis_.check_revision_lists(current_user)
    revision = {
        
        ('You' if revision.panelist == current_user else revision.panelist.full_name)\
            :revision.comment
        for revision in thesis_.revision_lists
    }

    return {'revision':revision}
