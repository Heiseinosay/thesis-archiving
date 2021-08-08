from types import MethodDescriptorType
from flask import Blueprint, render_template, request, flash, redirect, url_for
from werkzeug.exceptions import abort
from flask_login import login_required, current_user

from thesis_archiving import db

from thesis_archiving.utils import has_roles
from thesis_archiving.models import Group, User, Thesis
from thesis_archiving.validation import validate_input

from thesis_archiving.group.validation import CreateGroupSchema, UpdateGroupSchema

group = Blueprint("group", __name__, url_prefix="/group")

# create
# read 
# update
# delete

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
        return redirect(url_for('group.grading', group_id=group_id))
    except:
        flash("An error occured.","danger")

    return redirect(request.referrer)

@group.route("/grading/<int:group_id>", methods=['POST','GET'])
@login_required
@has_roles("is_adviser", "is_guest_panelist")
def grading(group_id):

    group_ = Group.query.get_or_404(group_id)
    
    if current_user not in group_.panelists:
        abort(403)

    if not group_.chairman:
        flash("Please assign a chairman before proceeding.", "danger")
        return redirect('user.profile')

    return render_template('group/grading.html')