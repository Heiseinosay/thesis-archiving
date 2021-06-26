from flask import Blueprint, render_template, request, redirect, url_for, send_file
from flask_login import login_required
from thesis_archiving.models import Thesis, User
from thesis_archiving.utils import export_to_excel
from sqlalchemy import or_

thesis = Blueprint("thesis", __name__, url_prefix="/thesis")

@thesis.route("/read")
@login_required
def read():
    # login req
    page = request.args.get('page', 1, type=int)
    search = '%' + request.args.get('search', '') + '%'
    
    theses = Thesis.query.filter(
                or_(
                    Thesis.title.like(search),
                    Thesis.area.like(search),
                    Thesis.keywords.like(search)
                )
            )

    # refine query by adviser and proponents if search query is not just the 2 wildcards
    if len(search) > 2:
        advisers = [a.id for a in User.query.filter_by(is_adviser=True).filter(or_(User.username.like(search), User.full_name.like(search))).all()]
        theses = theses.union_all(Thesis.query.filter(Thesis.adviser_id.in_(advisers)))
        
        # todo, proponents filtering

        # users = [u.id for u in User.query.filter_by(is_adviser=False).filter(or_(User.username.like(search), User.full_name.like(search))).all()]
        # theses = theses.union_all(Thesis.query.filter(Thesis.proponents.))

    theses = theses.order_by(Thesis.date_registered.desc()).order_by(Thesis.id.desc()).order_by(Thesis.number.desc()).paginate(page=page, per_page=25, error_out=False)

    return render_template("thesis/read.html", theses=theses)

@thesis.route("/export")
@login_required
def export():

    data = [ 
        [
            thesis.title,
            thesis.is_old,

            thesis.sy_start,
            thesis.semester,
            thesis.category.name,
            thesis.program.name,
            thesis.number,
            
            thesis.adviser.full_name,
            (''.join([user.username + ',' for user in thesis.proponents]))[:-1] if thesis.proponents.count() > 0 else None,

            thesis.area,
            thesis.keywords,
            thesis.date_deployed,

            thesis.overview
            
        ] for thesis in Thesis.query.order_by(Thesis.is_old, Thesis.title).all()
    ] 
    
    columns = [
        "title",
        "is_old",
        "sy_start",
        "semester",
        "category",
        "program",
        "number",
        "adviser",
        "proponents",
        "area",
        "keywords",
        "date_deployed",
        "overview"
    ]

    output, download_name = export_to_excel("thesis-archiving-thesis-", data, columns)

    return send_file(output, as_attachment=True, download_name=download_name)