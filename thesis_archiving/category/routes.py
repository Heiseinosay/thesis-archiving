from flask import Blueprint, render_template, request, flash, url_for, redirect
from flask_login import login_required

from sqlalchemy import or_

from thesis_archiving import db
from thesis_archiving.models import Category
from thesis_archiving.utils import has_roles

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