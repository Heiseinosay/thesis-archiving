from flask.templating import render_template
from thesis_archiving.models import QuantitativeCriteriaRating
from flask import Blueprint, request, flash, redirect

from flask_login import login_required

from thesis_archiving import db

from thesis_archiving.utils import has_roles
from thesis_archiving.validation import validate_input

from pprint import pprint

quantitative_criteria_rating = Blueprint("quantitative_criteria_rating", __name__, url_prefix="/quantitative_criteria_rating")

@quantitative_criteria_rating.route("/delete/<int:quantitative_criteria_rating_id>", methods=['POST'])
@login_required
@has_roles("is_admin")
def delete(quantitative_criteria_rating_id):
    
    quantitative_criteria_rating_ = QuantitativeCriteriaRating.query.get_or_404(quantitative_criteria_rating_id)
    
    try:
        db.session.delete(quantitative_criteria_rating_)
        db.session.commit()
        flash("Successfully deleted a quantitative criteria rating.", "success")
    except:
        flash("An error occured.","danger")

    return redirect(request.referrer)