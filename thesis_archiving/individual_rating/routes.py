from flask import Blueprint, render_template, request, flash, redirect, url_for
from werkzeug.exceptions import abort
from flask_login import login_required, current_user

from thesis_archiving import db

from thesis_archiving.utils import has_roles
from thesis_archiving.models import User, Thesis, IndividualRating

individual_rating = Blueprint("individual_rating", __name__, url_prefix="/individual_rating")

@individual_rating.route("/grading/<int:thesis_id>/<int:proponent_id>")
@login_required
@has_roles("is_adviser", "is_guest_panelist")
def grading(thesis_id, proponent_id):
    # check if thesis is valid
    thesis = Thesis.query.get_or_404(thesis_id)

    # check if user is a student
    proponent = User.query.filter_by(id=proponent_id, is_student=True).first_or_404()
    
    # check if user is thesis' proponent
    if proponent not in thesis.proponents:
        abort(406)
    
    # check if current user is panelist for the thesis
    if current_user not in thesis.group.panelists:
        abort(403)

    # Check if there is already an individual rating for the student 
    # if there is none, create a record for it
    individual_rating_ = proponent.check_student_individual_rating(
        student = proponent,
        thesis_id=thesis.id
        )

    return str(individual_rating_.id)

# @individual_rating.route("/grading/<int:thesis_id>/<int:individual_rating_id>", methods=["POST"])
# @login_required
# @has_roles("is_adviser, is_guest_panelist")
# def grading(thesis_id, individual_rating_id):

#     valid thesis 
#     proponent 

#     individual_rating_ = IndividualRating.query.get_or_404(individual_rating_id)

#     if not individual_rating_.check_thesis_id(thesis_id):
#         abort(403)



#     return individual_rating_.id



