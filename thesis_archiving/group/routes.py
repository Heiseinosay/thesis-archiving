from flask import Blueprint, render_template, request, flash, redirect, url_for
from werkzeug.exceptions import abort
from flask_login import login_required, current_user

from thesis_archiving import db

from thesis_archiving.utils import has_roles
from thesis_archiving.models import Group, IndividualRating, User, Thesis
from thesis_archiving.validation import validate_input

from thesis_archiving.group.validation import CreateGroupSchema, UpdateGroupSchema
from thesis_archiving.quantitative_rating.validation import ManuscriptGradeSchema
from thesis_archiving.group.utils import check_panelists

from pprint import pprint

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

    current_user.check_quantitative_panelist_grade(thesis_)

    quantitative_panelist_grade_ = current_user.quantitative_panelist_grades.filter_by(thesis_id=thesis_.id).first()

    individual_ratings = { 
        proponent.id : IndividualRating.query.filter_by(
            thesis_id=thesis_id, 
            student_id=proponent.id, 
            panelist_id=current_user.id
            ).first() for proponent in thesis_.proponents 
            }

    result = {
        "valid" : {},
        "invalid" : {}
    }

    if request.method == "POST":
        # contains form data converted to mutable dict
        data = request.form.to_dict()
        data["criteria"] = [ c.name for c in thesis_.quantitative_rating.criteria ]
        data["max_grade"] = thesis_.quantitative_rating.max_grade
        result = validate_input(data, ManuscriptGradeSchema)
    
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
        'group/grading.html', 
        thesis=thesis_,
        individual_ratings=individual_ratings,
        quantitative_panelist_grade=quantitative_panelist_grade_,
        result=result
        )
