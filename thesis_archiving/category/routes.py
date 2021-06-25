from flask import Blueprint, render_template, request
from flask_login import login_required
from thesis_archiving.models import Category
from sqlalchemy import or_

category = Blueprint("category", __name__, url_prefix="/category")

@category.before_request
@login_required

@category.route("/read")
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