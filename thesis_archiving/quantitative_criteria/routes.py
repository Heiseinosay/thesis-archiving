from thesis_archiving.models import QuantitativeCriteria
from flask import Blueprint, request, flash, redirect

from flask_login import login_required

from thesis_archiving import db

from thesis_archiving.utils import has_roles

quantitative_criteria = Blueprint("quantitative_criteria", __name__, url_prefix="/quantitative_criteria")

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