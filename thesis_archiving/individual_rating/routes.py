from flask import Blueprint, render_template, request, flash, redirect, url_for
from werkzeug.exceptions import abort
from flask_login import login_required, current_user

from thesis_archiving import db

from thesis_archiving.utils import has_roles
from thesis_archiving.models import User, Thesis, IndividualRating

individual_rating = Blueprint("individual_rating", __name__, url_prefix="/individual_rating")

@individual_rating.route("/check/<int:thesis_id>/<int:proponent_id>", methods=["POST"])
@login_required
@has_roles("is_adviser, is_guest_panelist")
def check(thesis_id, proponent_id):
    thesis = Thesis.query.get_or_404(thesis_id)
    proponent = User.query.filter_by(id=proponent_id, is_student=True).first_or_404()

    if proponent not in thesis.proponents:
        abort(406)
    
    if current_user not in thesis.group.panelists:
        abort(403)

    # Check if there is already an individual rating for the student before redirecting to its grading page
    # if there is none, create a record for it

    individual_rating_ = IndividualRating.query.filter_by(thesis_id=thesis_id, proponent_id=proponent_id, panelist_id=current_user.id).first_or_404():

    if not individual_rating_:
        individual_rating_ = IndividualRating()
        individual_rating_.thesis_id = thesis_id
        individual_rating_.student_id = proponent_id
        individual_rating_.panelist_id = current_user.id
        
        try:
            db.session.add(individual_rating_)
            db.session.commit()
            flash("Created new individual rating.",'success')
        except:
            flash("An error occured.",'danger')

    if individual_rating_:
        return redirect(url_for('individual_rating.grading', individual_rating_id=individual_rating_.id))
    
    flash("An error occured.",'danger')
    return redirect(request.referrer)

@individual_rating.route("/grading/<int:individual_rating_id>", methods=["POST"])
@login_required
@has_roles("is_adviser, is_guest_panelist")
def grading(individual_rating_id):

    individual_rating_ = IndividualRating.query.get_or_404(individual_rating_id)

    return individual_rating_.id