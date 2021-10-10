from flask import current_app
from thesis_archiving.models import User, Program, Category, Group, QuantitativeRating
from datetime import datetime
import pytz
import os

from PyPDF2 import PdfFileWriter, PdfFileReader
import io
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import letter

def select_choices():

    # pag bumagal yung site dahil dito,
    # change it na mafefetch yung needed choices lang

    choices_ = {
        'adviser_id' : {adviser.id : adviser.full_name for adviser in User.query.filter_by(is_adviser=True).order_by(User.full_name).all()},
        'program_id' : {program.id : program.name for program in Program.query.order_by(Program.name).all()},
        'category_id' : {category.id : category.name for category in Category.query.order_by(Category.name).all()},
        'sy_start' : { year : year for year in range(2000, datetime.now(tz=pytz.timezone('Asia/Manila')).year + 1)},
        'semester' : {1:1, 2:2},
        'is_old' : {1:'Old', 0:'New'},
        'group_id': { group.id:group.number for group in Group.query.order_by(Group.number).all() },
        'quantitative_rating_id': { rating.id:rating.name for rating in QuantitativeRating.query.order_by(QuantitativeRating.name.asc()).all()}
    }

    return choices_

def proposal_form_name(thesis, file):
    
    _ , f_ext = os.path.splitext(file.filename)
    
    return thesis.adviser.full_name + "-" + thesis.call_number() + f_ext

def save_proposal_form(thesis, file):
    
    # remove any existing
    remove_proposal_form(thesis)

    # create file name
    file_name = proposal_form_name(thesis, file)
    
    # stage to db the file name for commit
    thesis.proposal_form = file_name

    # root + year 
    path = os.path.join(
        current_app.root_path, 
        "static", 
        "thesis_attachments", 
        "proposal_form", 
        str(thesis.sy_start)
        )
    
    # creates directory for the year 
    if not os.path.exists(path):
        os.makedirs(path)
    
    # directory + filename
    path = os.path.join(path, thesis.proposal_form)

    # stamp w/ call number then save
    stamp_save(file, path, thesis.call_number())

def remove_proposal_form(thesis):

    proposal_form = thesis.proposal_form
    
    if proposal_form:
        path = os.path.join(
            current_app.root_path, 
            "static", 
            "thesis_attachments", 
            "proposal_form", 
            str(thesis.sy_start),
            proposal_form
            )

        if os.path.exists(path):
            os.remove(path)

def stamp_save(file, path, call_number):
    
    packet = io.BytesIO()

    # Create a new PDF with Reportlab
    can = canvas.Canvas(packet, pagesize=letter)

    can.setFillColorRGB(6/256,136/256,36/256)
    can.setFont('Helvetica-Bold', 18)
    can.drawString(410, 10, call_number)
    # can.drawString(410, 60, "2020-1-TPCS-58")
    can.showPage()
    can.save()

    # Move to the beginning of the StringIO buffer
    packet.seek(0)
    new_pdf = PdfFileReader(packet)

    # Read your existing PDF
    existing_pdf = PdfFileReader(file)
    output = PdfFileWriter()

    # Add the "watermark" (which is the new pdf) on the existing page
    page = existing_pdf.getPage(0)
    page.mergePage(new_pdf.getPage(0))
    output.addPage(page)

    # merge the rest
    for p in range(existing_pdf.getNumPages()):
        if p != 0:
            output.addPage(existing_pdf.getPage(p))

    # Finally, write "output" to a real file
    outputStream = open(path, "wb")
    output.write(outputStream)
    outputStream.close()