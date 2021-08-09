from flask import Blueprint, render_template, request, flash, redirect, url_for
# from werkzeug.exceptions import abort
from flask_login import login_required, current_user

from thesis_archiving import db, quantitative_rating

from thesis_archiving.utils import has_roles
from thesis_archiving.models import QuantitativeRating
from thesis_archiving.validation import validate_input

from thesis_archiving.quantitative_rating.validation import CreateQuantitativeRatingSchema

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