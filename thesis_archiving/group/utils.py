from flask import flash, redirect, render_template
from werkzeug.exceptions import abort
from xhtml2pdf import pisa
from io import StringIO, BytesIO
from datetime import datetime
import pytz

def check_panelists(current_user, group):
    
    if current_user not in group.panelists:
            abort(403)

    if not group.chairman:
        flash("Please assign a chairman before proceeding.", "danger")
        return redirect('user.profile')


def export_grading_docs(group, thesis, revision_list, individual_ratings, legend_25, legend_30, defense_rating, manuscript=None, developed_thesis=None):

    context = {
        "group":group, 
        "thesis":thesis, 
        "date": datetime.now(tz=pytz.timezone('Asia/Manila')).strftime("%B %d, %Y"),
        "revision_list":revision_list, 
        "individual_ratings":individual_ratings,
        "legend_25":legend_25,
        "legend_30":legend_30,
        "defense_rating":defense_rating
    }

    if manuscript:
        context["manuscript"] = manuscript
    
    if developed_thesis:
        context["developed_thesis"] = developed_thesis

    html = render_template("grading_docs/docs.html", **context)

    pdf = BytesIO()
    
    pisa.CreatePDF(StringIO(html), pdf)

    pdf = pdf.getvalue()
    
    headers = {
        'content-type': 'application.pdf',
        'content-disposition': f'inline; filename={thesis.call_number() + " defense"}.pdf'}
    
    return pdf, 200, headers