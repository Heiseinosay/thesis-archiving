from flask import (
    Blueprint, 
    render_template, 
    request, 
    flash, 
    redirect, 
    url_for, 
    abort, 
    jsonify, 
    make_response
)

from werkzeug.exceptions import abort
import time
from flask_login import login_required, current_user

from thesis_archiving import db

from thesis_archiving.utils import has_roles
from thesis_archiving.models import User, Thesis, IndividualRating

from thesis_archiving.individual_rating.validation import IndividualRatingSchema

from pprint import pprint

from thesis_archiving.validation import validate_input

individual_rating = Blueprint("individual_rating", __name__, url_prefix="/individual_rating")

@individual_rating.route("/grading/<int:thesis_id>/<int:proponent_id>", methods=["POST","GET"])
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
    # returns individual rating
    individual_rating_ = proponent.check_student_individual_rating(
        student = proponent,
        thesis_id=thesis.id,
        panelist_id=current_user.id

        )

    result = {
        'valid' : {},
        'invalid' : {}
    }

    # if request.method == "POST":
        
    #     # contains form data converted to mutable dict
    #     data = request.form.to_dict()
    #     result = validate_input(data, IndividualRatingSchema)

    #     if not result["invalid"]:
            
    #         data = result["valid"]

    #         if data.get("intelligent_response"):
    #             individual_rating_.intelligent_response = data["intelligent_response"]
            
    #         if data.get("respectful_response"):
    #             individual_rating_.respectful_response = data["respectful_response"]

    #         if data.get("communication_skills"):
    #             individual_rating_.communication_skills = data["communication_skills"]

    #         if data.get("confidence"):
    #             individual_rating_.confidence = data["confidence"]

    #         if data.get("attire"):
    #             individual_rating_.attire = data["attire"]

    #         individual_rating_.is_final = data["is_final"] if data.get("is_final") else False

    #         try:
    #             db.session.commit()
    #             flash("Successfully graded.","success")
    #         except:
    #             flash("An error occured while trying to grade.","danger")
    # submit for SAVE
    # submit for GRADING (is_final) boolean nalang to lol checkable
    # CONFIRMATION MODALS
    # print din kung ano yung value na nakukuha

    return render_template("individual_rating/grading.html", individual_rating=individual_rating_, result=result)

@individual_rating.route("/ajax-grading/<int:thesis_id>/<int:proponent_id>", methods=['POST', 'GET'])
@login_required
@has_roles("is_adviser", "is_guest_panelist")
def ajax_grading(thesis_id, proponent_id):

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
    # returns individual rating
    
    individual_rating_ = proponent.check_student_individual_rating(
        student = proponent,
        thesis_id=thesis.id,
        panelist_id=current_user.id

        )
    
    result = {
        'valid' : {},
        'invalid' : {}
    }


    if request.method == 'POST':
        
        # contains form data converted to mutable dict
        data = request.form.to_dict()
        result = validate_input(data, IndividualRatingSchema)

        if not result["invalid"]:
            
            data = result["valid"]

            if data.get("intelligent_response"):
                individual_rating_.intelligent_response = data["intelligent_response"]
            
            if data.get("respectful_response"):
                individual_rating_.respectful_response = data["respectful_response"]

            if data.get("communication_skills"):
                individual_rating_.communication_skills = data["communication_skills"]

            if data.get("confidence"):
                individual_rating_.confidence = data["confidence"]

            if data.get("attire"):
                individual_rating_.attire = data["attire"]

            individual_rating_.is_final = data["is_final"] if data.get("is_final") else False

            try:
                db.session.commit()
            except:
                abort(500)
    
    individual_rating_ = {
        "intelligent_response" : individual_rating_.intelligent_response,
        "respectful_response" : individual_rating_.respectful_response,
        "communication_skills" : individual_rating_.communication_skills,
        "confidence" : individual_rating_.confidence,
        "attire" : individual_rating_.attire,
        "is_final" : individual_rating_.is_final
    }

    if result['invalid']:
        return jsonify(result), 406

    return jsonify({'result': result, 'individual_rating': individual_rating_})

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



