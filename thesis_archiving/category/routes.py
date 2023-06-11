from flask import Blueprint, render_template, request, flash, url_for, redirect
from flask_login import login_required

from sqlalchemy import or_

from thesis_archiving import db
from thesis_archiving.models import Category
from thesis_archiving.utils import has_roles
from thesis_archiving.validation import validate_input

from thesis_archiving.category.validation import CreateCategorySchema, UpdateCategorySchema

category = Blueprint("category", __name__, url_prefix="/category")

@category.route("/read")
@login_required
@has_roles("is_admin")
def read():
    page = request.args.get('page', 1, type=int)
    search = '%' + request.args.get('search', '') + '%'
    
    categories = Category.query.filter(
            or_(
                Category.name.like(search),
                Category.code.like(search)
            )
        ).order_by(Category.name).paginate()

    return render_template("category/read.html", categories=categories)

@category.route("/create", methods=["POST","GET"])
@login_required
@has_roles("is_superuser")
def create():
    result = {
        'valid' : {},
        'invalid' : {}
    }

    if request.method == "POST":
        
        # contains form data converted to mutable dict
        data = request.form.to_dict()
        
        # marshmallow validation
        result = validate_input(data, CreateCategorySchema)

        if not result['invalid']:
            # prevent premature flushing
            with db.session.no_autoflush:
                # values for validated and filtered input
                data = result['valid']
                
                # init model obj + fill in values
                _category = Category()

                _category.name = data['name']
                _category.code = data['code']

                try:
                    db.session.add(_category)
                    db.session.commit()
                    flash("Successfully created new category.", "success")
                    return redirect(url_for('category.read'))

                except:
                    flash("An error occured", "danger")

    return render_template("category/create.html", result=result)

@category.route("/update/<int:category_id>", methods=["POST", "GET"])
@login_required
@has_roles("is_admin")
def update(category_id):

    _category = Category.query.get_or_404(category_id)

    result = {
        'valid' : {},
        'invalid' : {}
    }

    if request.method == "POST":
        # contains form data converted to mutable dict
        data = request.form.to_dict()
        
        
        # marshmallow validation
        result = validate_input(data, UpdateCategorySchema, category_obj=_category)

        if not result['invalid']:
            # prevent premature flushing
            with db.session.no_autoflush:
                # values for validated and filtered input
                data = result['valid']

                _category.name = data['name']
                _category.code = data['code']

                try:
                    db.session.commit()
                    flash("Successfully updated category.", "success")
                    return redirect(request.referrer)

                except:
                    flash("An error occured", "danger")

    return render_template("category/update.html", result=result, category=_category)

@category.route("/delete/<int:category_id>", methods=["POST"])
@login_required
@has_roles("is_superuser")
def delete(category_id):
    _category = Category.query.get_or_404(category_id)
    
    try:
        db.session.delete(_category)
        db.session.commit()
        flash("Successfully deleted a category.","success")
        
        return redirect(request.referrer)
    except:
        flash("An error occured.","danger")

    return redirect(url_for('category.read'))