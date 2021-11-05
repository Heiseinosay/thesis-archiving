from flask import Blueprint, render_template, request, flash, redirect, url_for, abort

from flask_login import login_required, current_user
from sqlalchemy import and_

from thesis_archiving import db

from thesis_archiving.utils import has_roles
from thesis_archiving.models import QuantitativeRating, QuantitativeCriteria, QuantitativePanelistGrade, QuantitativeCriteriaGrade, Group, Thesis
from thesis_archiving.validation import validate_input

from thesis_archiving.quantitative_rating.validation import CreateQuantitativeRatingSchema, UpdateQuantitativeRatingSchema, ManuscriptGradeSchema

from thesis_archiving.group.utils import check_panelists

from pprint import pprint

quantitative_rating = Blueprint("quantitative_rating", __name__, url_prefix="/quantitative_rating")

@quantitative_rating.route("/read")
@login_required
@has_roles("is_admin")
def read():

    page = request.args.get('page', 1, type=int)
    search = '%' + request.args.get('search', '') + '%'

    quantitative_ratings = QuantitativeRating.query\
        .filter(QuantitativeRating.name.like(search))\
        .order_by(QuantitativeRating.name)\
        .paginate(error_out=False)

    return render_template('quantitative_rating/read.html', quantitative_ratings=quantitative_ratings)

@quantitative_rating.route("/create", methods=['POST','GET'])
@login_required
@has_roles("is_admin")
def create():

    result = {
        'valid' : {},
        'invalid' : {}
    }

    if request.method == 'POST':
        # contains form data converted to mutable dict
        data = request.form.to_dict()
        
        # marshmallow validation
        result = validate_input(data, CreateQuantitativeRatingSchema)

        if not result['invalid']:
            # prevent premature flushing
            with db.session.no_autoflush:
                # values for validated and filtered input
                data = result['valid']

                quantitative_rating_ = QuantitativeRating()

                quantitative_rating_.name = data['name']

                try:
                    db.session.add(quantitative_rating_)
                    db.session.commit()
                    flash("Successfully created a new quantitative rating.", "success")
                    return redirect(url_for('quantitative_rating.read'))

                except:
                    flash("An error occured", "danger")


    return render_template('quantitative_rating/create.html', result=result)

@quantitative_rating.route("/update/<int:quantitative_rating_id>", methods=['POST','GET'])
@login_required
@has_roles("is_admin")
def update(quantitative_rating_id):

    quantitative_rating_ = QuantitativeRating.query.get_or_404(quantitative_rating_id)

    result = {
        'valid' : {},
        'invalid' : {}
    }

    if request.method == 'POST':
        # contains form data converted to mutable dict
        data = request.form.to_dict()
        
        # remove empty item
        if not data['criteria_name']:
            data.pop('criteria_name')

        # marshmallow validation
        result = validate_input(data, UpdateQuantitativeRatingSchema, quantitative_rating_obj=quantitative_rating_)

        if not result['invalid']:

            # prevent premature flushing
            with db.session.no_autoflush:

                # values for validated and filtered input
                data = result['valid']

                quantitative_rating_.name = data['name']
                quantitative_rating_.max_grade = data['max_grade']

                if data.get('criteria_name'):

                    # create a new criteria to append to the quanti rating
                    quantitative_criteria_ = QuantitativeCriteria()
                    quantitative_criteria_.name = data['criteria_name']
                    
                    quantitative_rating_.criteria.append(quantitative_criteria_)

                try:
                    db.session.commit()
                    flash("Successfully updated quantitative rating.", "success")
                    return redirect(request.referrer)

                except:
                    flash("An error occured", "danger")


    return render_template('quantitative_rating/update.html', result=result, quantitative_rating=quantitative_rating_)

@quantitative_rating.route("/grading/<int:group_id>/<int:thesis_id>/<int:quantitative_rating_id>", methods=['POST','GET'])
@login_required
@has_roles("is_adviser", "is_guest_panelist")
def grading(group_id, thesis_id, quantitative_rating_id):

    group_ = Group.query.get_or_404(group_id)
    thesis_ = Thesis.query.get_or_404(thesis_id)
    
    check_panelists(current_user, group_)

    if thesis_ not in group_.presentors:
        abort(406)
    
    quantitative_rating_ = QuantitativeRating.query.get_or_404(quantitative_rating_id)

    # if not in either manuscript or developed
    if not (thesis_ in quantitative_rating_.theses or thesis_ in quantitative_rating_.developed_theses):
        abort(406)

    current_user.check_quantitative_panelist_grade(thesis_, quantitative_rating_)

    quantitative_panelist_grade_ = db.session.query(QuantitativePanelistGrade).where(
			and_(
					# get the panelist id who graded those criteria
					QuantitativePanelistGrade.id.in_(
						db.session.query(QuantitativeCriteriaGrade.quantitative_panelist_grade_id).where(
							# get id of grades pointing to those criteria
							QuantitativeCriteriaGrade.quantitative_criteria_id.in_(
								# obtain all id ng MANUSCRIPT rating criteria ng thesis
								db.session.query(QuantitativeCriteria.id).where(QuantitativeCriteria.quantitative_rating_id == quantitative_rating_.id)        
							)
						)
					),
					QuantitativePanelistGrade.thesis_id == thesis_.id,
					QuantitativePanelistGrade.panelist_id == current_user.id
				)
			).first()
    
    result = {
        "valid": {},
        "invalid": {}
    }

    if request.method == "POST":
        # contains form data converted to mutable dict
        data = request.form.to_dict()
        data["criteria"] = [ c.name for c in quantitative_rating_.criteria ]
        data["max_grade"] = quantitative_rating_.max_grade
        
        result = validate_input(data, ManuscriptGradeSchema)
        
        if not result['invalid']:

            # prevent premature flushing
            with db.session.no_autoflush:

                # values for validated and filtered input
                data = result['valid']

                # loop over each QuantitativeCriteriaGrade of the panelist
                for grade in quantitative_panelist_grade_.grades:
                    
                    criteria_name = grade.criteria.name
                    
                    # update grade if scored
                    if criteria_name in data["grades"]:
                        grade.grade = data["grades"][criteria_name]

                quantitative_panelist_grade_.is_final = data["is_final"]
                
                try:
                    db.session.commit()
                    flash("Successfully graded quantitative rating.", "success")
                    return redirect(request.referrer)

                except:
                    flash("An error occured", "danger")

    # revision textarea
    # unahin muna revision list + saving dahil mas madali
    # CONFIRMATION MODALS

    # post process error msg for each grade
    invalid_grades = result["invalid"]["grades"] if result["invalid"].get("grades") else None
    if invalid_grades:
        # list() to create a copy of keys and prevent runtime error dict size changing
        for g in list(invalid_grades):
            result["invalid"][g] = result["invalid"]["grades"].pop(g)

    # post process success msg for each grade
    valid_grades = result["valid"]["grades"] if result["valid"].get("grades") else None
    if valid_grades:
        for g in list(valid_grades):
            result["valid"][g] = result["valid"]["grades"].pop(g)

    return render_template(
        'quantitative_rating/grading.html', 
        thesis=thesis_,
        quantitative_rating=quantitative_rating_,
        quantitative_panelist_grade=quantitative_panelist_grade_,
        result=result
        )



@quantitative_rating.route("/delete/<int:quantitative_rating_id>", methods=['POST'])
@login_required
@has_roles("is_admin")
def delete(quantitative_rating_id):

    quantitative_rating_ = QuantitativeRating.query.get_or_404(quantitative_rating_id)

    try:
        db.session.delete(quantitative_rating_)
        db.session.commit()
        flash("Successfully deleted a quantitative rating.", "success")

    except:
        flash("An error occured", "danger")
    
    return redirect(url_for('quantitative_rating.read'))