from flask import Blueprint, render_template, request, flash, redirect, url_for

from flask_login import login_required

from thesis_archiving import db

from thesis_archiving.utils import has_roles
from thesis_archiving.models import QuantitativeRating, QuantitativeCriteria
from thesis_archiving.validation import validate_input

from thesis_archiving.quantitative_rating.validation import CreateQuantitativeRatingSchema, UpdateQuantitativeRatingSchema

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