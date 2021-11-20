from flask import Blueprint, render_template, request, flash, redirect, url_for
from werkzeug.exceptions import abort
from flask_login import login_required, current_user

from thesis_archiving import db

from thesis_archiving.utils import has_roles, get_quantitative_panelist_grade
from thesis_archiving.models import Group, IndividualRating, RevisionList, User, Thesis, QuantitativePanelistGrade
from thesis_archiving.validation import validate_input

from thesis_archiving.group.validation import CreateGroupSchema, UpdateGroupSchema, UpdateRevisionSchema
from thesis_archiving.group.utils import check_panelists, export_grading_docs

from pprint import pprint
from num2words import num2words as nw

group = Blueprint("group", __name__, url_prefix="/group")

@group.route("/create", methods=["POST","GET"])
@login_required
@has_roles("is_admin")
def create():
    
    # recommended number
    # grab first result sorted by number column in descending
    num = Group.query.order_by(Group.number.desc()).first()
    num = num.number + 1 if num else 1
    
    result = {
        'valid' : {},
        'invalid' : {}
    }

    if request.method == 'POST':
        # contains form data converted to mutable dict
        data = request.form.to_dict()
        
        # marshmallow validation
        result = validate_input(data, CreateGroupSchema)

        if not result['invalid']:
            # prevent premature flushing
            with db.session.no_autoflush:
                data = result['valid']

                group_ = Group()

                group_.number = data['number']

                try:
                    db.session.add(group_)
                    db.session.commit()
                    flash("Successfully created new group.", "success")
                    return redirect(url_for('group.read'))

                except:
                    flash("An error occured", "danger")


    return render_template("group/create.html", result=result, num=num)

@group.route("/read")
@login_required
@has_roles("is_admin")
def read():
    
    groups = Group.query.order_by(Group.number)

    return render_template("group/read.html", groups=groups)

@group.route("/update/<int:group_id>", methods=['POST','GET'])
@login_required
@has_roles("is_admin")
def update(group_id):
    
    group_ = Group.query.get_or_404(group_id)

    result = {
        'valid' : {},
        'invalid' : {}
    }

    if request.method == 'POST':
        # contains form data converted to mutable dict
        data = request.form.to_dict()
        
        # remove empty item
        if not data['panelist_username']:
            data.pop('panelist_username')
        
        # marshmallow validation
        result = validate_input(data, UpdateGroupSchema, group_obj=group_)

        if not result['invalid']:
            # prevent premature flushing
            with db.session.no_autoflush:

                group_.number = data['number']

                if data.get('panelist_username'):
                    user_ = User.query.filter_by(username=data['panelist_username']).first()
                    group_.panelists.append(user_)

                try:
                    db.session.commit()
                    flash("Successfully updated group.", "success")
                except:
                    flash("An error occured", "danger")

    return render_template("group/update.html", group=group_, result=result)

@group.route("/delete/<int:group_id>", methods=['POST'])
@login_required
@has_roles("is_admin")
def delete(group_id):
    
    group_ = Group.query.get_or_404(group_id)

    try:
        db.session.delete(group_)
        db.session.commit()
        flash("Successfully deleted a group.","success")
        return redirect(url_for('group.read'))
    except:
        flash("An error occured.","danger")

    return redirect(url_for('group.read'))

@group.route("/remove/panelist/<int:group_id>/<int:user_id>", methods=['POST'])
@login_required
@has_roles("is_admin")
def panelist_remove(group_id, user_id):
    
    group_ = Group.query.get_or_404(group_id)
    user_ = User.query.get_or_404(user_id)
    
    try:
        group_.panelists.remove(user_)
        db.session.commit()
        flash("Successfully removed a panelist.","success")
        return redirect(request.referrer)
    except:
        flash("An error occured.","danger")

    return redirect(request.referrer)

@group.route("/remove/presentor/<int:group_id>/<int:thesis_id>", methods=['POST'])
@login_required
@has_roles("is_admin")
def presentor_remove(group_id, thesis_id):
    
    group_ = Group.query.get_or_404(group_id)
    thesis_ = Thesis.query.get_or_404(thesis_id)
    
    try:
        group_.presentors.remove(thesis_)
        db.session.commit()
        flash("Successfully removed a presentor.","success")
        return redirect(request.referrer)
    except:
        flash("An error occured.","danger")

    return redirect(request.referrer)

@group.route("/assign/chairman/<int:group_id>", methods=['POST'])
@login_required
@has_roles("is_adviser", "is_guest_panelist")
def chairman_assign(group_id):

    group_ = Group.query.get_or_404(group_id)

    try:
        group_.chairman = current_user
        db.session.commit()
        flash("Successfully assigned as chairman.","success")
        return redirect(url_for('group.presentors', group_id=group_id))
    except:
        flash("An error occured.","danger")

    return redirect(request.referrer)

@group.route("/presentors/<int:group_id>", methods=['POST','GET'])
@login_required
@has_roles("is_adviser", "is_guest_panelist")
def presentors(group_id):

    group_ = Group.query.get_or_404(group_id)
    
    check_panelists(current_user, group_)

    return render_template('group/presentors.html', group=group_)

@group.route("/grading/<int:group_id>/<int:thesis_id>", methods=['POST','GET'])
@login_required
@has_roles("is_adviser", "is_guest_panelist")
def grading(group_id, thesis_id):

    group_ = Group.query.get_or_404(group_id)
    thesis_ = Thesis.query.get_or_404(thesis_id)
    
    check_panelists(current_user, group_)

    if thesis_ not in group_.presentors:
        abort(406)

    individual_ratings = { 
        proponent.id : IndividualRating.query.filter_by(
            thesis_id=thesis_id, 
            student_id=proponent.id, 
            panelist_id=current_user.id
            ).first() for proponent in thesis_.proponents 
            }
    
    qualitative_ratings = {
        None : None,
        "PASSED" : "A “Passed” qualitative rating is given if the panel members perceived that the project satisfactorily met all criteria.",
        "CONDITIONAL PASS" : "This rating is a borderline between \"Pass\" and \"Redefense\" remarks. This rating may be given if the panel members viewed that 1) the project/paper needs revisions, 2) the revisions can be done within three days, and 3) there is a need to present the revisions to at least one of the panel members.",
        "REDEFENSE" : "If the following conditions are met, then the rating \"Redefense\" is justifiable: 1) the project/paper needs revisions, 2) the revisions require one week to comply, and 3) the panel members feel that there is a need to present the revisions to the three-man committee.",
        "FAILED" : "The project/paper did not satisfactorily meet all of the criteria. For the Software Project Stage, the minimum requirements are not satisfied."
    }
        

    panelist_grades = [grade.is_final for grade in thesis_.quantitative_panelist_grades.filter_by(panelist_id=current_user.id).all()]

    quantitative_status = all(panelist_grades) if len(panelist_grades) > 0 else False
    
    revision = thesis_.check_revision_lists(current_user)

    result = {
        "valid" : {},
        "invalid" : {}
    }

    if request.method == "POST":
        if request.form["form_name"] == "qualitative" and request.form.get("qualitative_rating") in ["PASSED", "CONDITIONAL PASS", "REDEFENSE", "FAILED"]:
            # make necessary checks before commiting to new rating
            # make necessary checks before generating docs

            not_final = []
            
            for panelist in group_.panelists:

                # if some of the grading component is not final yet
                if thesis_.quantitative_panelist_grades.filter(QuantitativePanelistGrade.is_final != True, QuantitativePanelistGrade.panelist_id == panelist.id).all()\
                    or thesis_.individual_rating_panelist_grades.filter(IndividualRating.is_final != True, IndividualRating.panelist_id == panelist.id).all()\
                        or thesis_.revision_lists.filter(RevisionList.is_final != True, RevisionList.panelist_id == panelist.id).all():
                    not_final.append(panelist.full_name)

            if not_final:
                flash("The following panelists are not yet done grading: " + ", ".join(map(str,not_final)) ,"warning")
            else:
                
                legend_25 = {
                    0 : {"grade" : 0, "equivalent" : 0},
                    1 : {"grade" : 52, "equivalent" : 5.00},
                    2 : {"grade" : 54, "equivalent" : 5.00},
                    3 : {"grade" : 56, "equivalent" : 5.00},
                    4 : {"grade" : 58, "equivalent" : 5.00},
                    5 : {"grade" : 60, "equivalent" : 5.00},
                    6 : {"grade" : 62, "equivalent" : 5.00},
                    7 : {"grade" : 64, "equivalent" : 5.00},
                    8 : {"grade" : 66, "equivalent" : 5.00},
                    9 : {"grade" : 68, "equivalent" : 5.00},
                    10 : {"grade" : 70, "equivalent" : 5.00},
                    11 : {"grade" : 72, "equivalent" : 5.00},
                    12 : {"grade" : 74, "equivalent" : 5.00 },
                    13 : {"grade" : 76, "equivalent" : 3.00 },
                    14 : {"grade" : 78, "equivalent" : 2.75 },
                    15 : {"grade" : 80, "equivalent" : 2.5 },
                    16 : {"grade" : 82, "equivalent" : 2.5 },
                    17 : {"grade" : 84, "equivalent" : 2.25 },
                    18 : {"grade" : 86, "equivalent" : 2.00 },
                    19 : {"grade" : 88, "equivalent" : 2.00 },
                    20 : {"grade" : 90, "equivalent" : 1.75 },
                    21 : {"grade" : 92, "equivalent" : 1.5 },
                    22 : {"grade" : 94, "equivalent" : 1.5 },
                    23 : {"grade" : 96, "equivalent" : 1.25 },
                    24 : {"grade" : 98, "equivalent" : 1.00 },
                    25 : {"grade" : 100, "equivalent" : 1.00 },
                }

                legend_30 = {
                    0: {"grade" : 0, "equivalent" : 0},
                    1: {"grade" : 52, "equivalent" : 5.00},
                    2: {"grade" : 53, "equivalent" : 5.00},
                    3: {"grade" : 55, "equivalent" : 5.00},
                    4: {"grade" : 57, "equivalent" : 5.00},
                    5: {"grade" : 58, "equivalent" : 5.00},
                    6: {"grade" : 60, "equivalent" : 5.00},
                    7: {"grade" : 62, "equivalent" : 5.00},
                    8: {"grade" : 63, "equivalent" : 5.00},
                    9: {"grade" : 65 , "equivalent" : 5.00},
                    10: {"grade" :67 , "equivalent" : 5.00},
                    11: {"grade" :68 , "equivalent" : 5.00},
                    12: {"grade" :70 , "equivalent" : 5.00},
                    13: {"grade" :72 , "equivalent" : 5.00},
                    14: {"grade" :73 , "equivalent" : 5.00},
                    15: {"grade" :75 , "equivalent" : 3},
                    16: {"grade" :77 , "equivalent" : 3},
                    17: {"grade" :78 , "equivalent" : 2.75},
                    18: {"grade" :80 , "equivalent" : 2.5},
                    19: {"grade" :82 , "equivalent" : 2.5},
                    20: {"grade" :83 , "equivalent" : 2.25},
                    21: {"grade" :85 , "equivalent" : 2.25},
                    22: {"grade" :87 , "equivalent" : 2},
                    23: {"grade" :88 , "equivalent" : 2},
                    24: {"grade" :90 , "equivalent" : 1.75},
                    25: {"grade" : 92, "equivalent" : 1.5},
                    26: {"grade" : 93, "equivalent" : 1.5},
                    27: {"grade" : 95, "equivalent" : 1.25},
                    28: {"grade" : 97, "equivalent" : 1.25},
                    29: {"grade" : 98, "equivalent" : 1},
                    30: {"grade" : 100, "equivalent" : 1}
                }

                weights = { "developed_thesis" : 0.7, "manuscript" : 0.3 }

                revision_list = {}

                individual_ratings = {}
                
                manuscript = {}
                manuscript_query = get_quantitative_panelist_grade(thesis_.quantitative_rating_id, thesis_.id) if thesis_.quantitative_rating_id else None

                developed_thesis = {}
                developed_thesis_query = get_quantitative_panelist_grade(thesis_.quantitative_rating_developed_id, thesis_.id) if thesis_.quantitative_rating_developed_id else None

                defense_rating = {
                    "rating" : 0,
                    "words" : "",
                }

                for panelist in group_.panelists:
                    
                    revision_list[panelist] = thesis_.revision_lists.filter_by(panelist_id=panelist.id).first()
                    
                    individual_ratings[panelist] = {}
                    
                    for proponent in thesis_.proponents:
                        
                        individual_ratings[panelist][proponent.username + ' - ' + proponent.full_name] = {}
                        
                        # function to get the grade for criteria
                        get_grade = lambda criteria : criteria if criteria else 0

                        # fetch the proponent's individual rating for the thesis
                        grades = thesis_.individual_rating_panelist_grades.filter_by(student_id=proponent.id, panelist_id=panelist.id).first()
                        
                        individual_ratings[panelist][proponent.username + ' - ' + proponent.full_name]["grades"] = grades
                        individual_ratings[panelist][proponent.username + ' - ' + proponent.full_name]["total"] = get_grade(grades.intelligent_response) + get_grade(grades.respectful_response) + get_grade(grades.communication_skills) + get_grade(grades.confidence) + get_grade(grades.attire)

                        total = individual_ratings[panelist][proponent.username + ' - ' + proponent.full_name]["total"]

                        individual_ratings[panelist][proponent.username + ' - ' + proponent.full_name]["legend"] = legend_25[total]
                    
                    if thesis_.quantitative_rating_id:
                        
                        manuscript[panelist] = {}

                        manuscript[panelist]["grades"] = manuscript_query.filter_by(panelist_id = panelist.id).first()

                        total = 0

                        for grade in manuscript[panelist]["grades"].grades:
                            total += grade.grade
                             
                        manuscript[panelist]["total"] = total
                        manuscript[panelist]["legend"] = legend_25[total] if thesis_.manuscript_rating.criteria.count() == 5 else legend_30[total]
                        manuscript[panelist]["weighted"] = round(manuscript[panelist]["legend"]["grade"] * ( 0.3 if thesis_.quantitative_rating_developed_id else 1), 2)

                        defense_rating["rating"] += manuscript[panelist]["weighted"]

                    if thesis_.quantitative_rating_developed_id:

                        developed_thesis[panelist] = {}
                        
                        developed_thesis[panelist]["grades"] = developed_thesis_query.filter_by(panelist_id = panelist.id).first()

                        total = 0

                        for grade in developed_thesis[panelist]["grades"].grades:
                            total += grade.grade
                             
                        developed_thesis[panelist]["total"] = total
                        developed_thesis[panelist]["legend"] = legend_25[total] if thesis_.developed_thesis_rating.criteria.count() == 5 else legend_30[total]
                        developed_thesis[panelist]["weighted"] = round(developed_thesis[panelist]["legend"]["grade"] * 0.7,2)

                        defense_rating["rating"] += developed_thesis[panelist]["weighted"]
                    
                defense_rating["rating"] = round(defense_rating["rating"] / group_.panelists.count(), 2)
                defense_rating["words"] = nw(round(defense_rating["rating"], 2))

                    
                thesis_.qualitative_rating = request.form.get("qualitative_rating")
                
                # try:
                db.session.commit()
                return export_grading_docs(
                    group_, 
                    thesis_, 
                    revision_list, 
                    individual_ratings, 
                    legend_25,
                    legend_30,
                    defense_rating,
                    manuscript if manuscript else None,
                    developed_thesis if developed_thesis else None
                    )
                # except:
                #     flash("An error occured while trying to generate documents.","danger")

        elif request.form["form_name"] == "revision":
            # contains form data converted to mutable dict
            data = request.form.to_dict()
            data.pop("form_name")
                    
            result = validate_input(data, UpdateRevisionSchema)
            if not result['invalid']:
                # prevent premature flushing
                with db.session.no_autoflush:

                    # values for validated and filtered input
                    data = result['valid']

                    revision.comment = data["comment"]
                    revision.is_final = data["is_final"] if data.get("is_final") else False
                    
                    try:
                        db.session.commit()
                        flash("Successfully saved revision.", "success")
                        return redirect(request.referrer)

                    except:
                        flash("An error occured", "danger")
    
    return render_template(
        'group/grading.html', 
        thesis=thesis_,
        individual_ratings=individual_ratings,
        quantitative_status=quantitative_status,
        revision = revision,
        result = result,
        group = group_,
        qualitative_ratings = qualitative_ratings
        )
