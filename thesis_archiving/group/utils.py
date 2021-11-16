from flask import flash, redirect, render_template
from werkzeug.exceptions import abort
from xhtml2pdf import pisa
from io import StringIO, BytesIO

def check_panelists(current_user, group):
    
    if current_user not in group.panelists:
            abort(403)

    if not group.chairman:
        flash("Please assign a chairman before proceeding.", "danger")
        return redirect('user.profile')


def export_grading_docs(panelists, thesis, revision_list, individual_ratings, legend, manuscript=None, developed_thesis=None):

    context = {
        "panelists":panelists, 
        "thesis":thesis, 
        "revision_list":revision_list, 
        "individual_ratings":individual_ratings,
        "legend":legend
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
        'content-disposition': 'inline; filename=certificate.pdf'}
    
    return pdf, 200, headers