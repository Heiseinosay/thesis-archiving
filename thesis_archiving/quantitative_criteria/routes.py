from flask.templating import render_template
from thesis_archiving.models import QuantitativeCriteria, QuantitativeCriteriaRating
from flask import Blueprint, request, flash, redirect

from flask_login import login_required

from thesis_archiving import db

from thesis_archiving.utils import has_roles
from thesis_archiving.validation import validate_input

from thesis_archiving.quantitative_criteria.validation import UpdateQuantitativeCriteria

from pprint import pprint

quantitative_criteria = Blueprint("quantitative_criteria", __name__, url_prefix="/quantitative_criteria")

@quantitative_criteria.route("/update/<int:quantitative_criteria_id>", methods=['POST',"GET"])
@login_required
@has_roles("is_admin")
def update(quantitative_criteria_id):
    
    quantitative_criteria_ = QuantitativeCriteria.query.get_or_404(quantitative_criteria_id)
    
    result = {
        "valid" : {},
        "invalid" : {}
    }

    if request.method == "POST":
        # contains form data converted to mutable dict
        data = request.form.to_dict()
        
        if not data["description"]:
            data.pop("description")
        
        # if no rating, rating desc is no use
        if not data["rating_rate"]:
            data.pop("rating_rate")
            data.pop("rating_description")
        
        # marshmallow validation
        result = validate_input(
            data, 
            UpdateQuantitativeCriteria, 
            quantitative_criteria_obj=quantitative_criteria_,
            max_grade=quantitative_criteria_.rating.max_grade
            )

        if not result['invalid']:

            # prevent premature flushing
            with db.session.no_autoflush:

                # values for validated and filtered input
                data = result['valid']

                quantitative_criteria_.name = data["name"]
                quantitative_criteria_.description = data.get("description")

                if data.get("rating_rate"):
                    quantitative_criteria_rating_ = QuantitativeCriteriaRating()
                    quantitative_criteria_rating_.rate = data["rating_rate"]
                    quantitative_criteria_rating_.description = data["rating_description"]

                    quantitative_criteria_.ratings.append(quantitative_criteria_rating_)

                try:
                    db.session.commit()
                    flash("Successfully updated quantitative criteria.", "success")
                    return redirect(request.referrer)

                except:
                    flash("An error occured", "danger")

    return render_template("quantitative_criteria/update.html", quantitative_criteria=quantitative_criteria_, result=result)

@quantitative_criteria.route("/delete/<int:quantitative_criteria_id>", methods=['POST'])
@login_required
@has_roles("is_admin")
def delete(quantitative_criteria_id):
    
    quantitative_criteria_ = QuantitativeCriteria.query.get_or_404(quantitative_criteria_id)
    
    try:
        db.session.delete(quantitative_criteria_)
        db.session.commit()
        flash("Successfully deleted a quantitative criteria and grades associated.", "success")
    except:
        flash("An error occured.","danger")

    return redirect(request.referrer)