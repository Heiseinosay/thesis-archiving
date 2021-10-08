from flask import current_app
from thesis_archiving.models import User, Program, Category, Group, QuantitativeRating
from datetime import datetime
import pytz
import os

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
    
    # root + year 
    path = os.path.join(
        current_app.root_path, 
        "static", 
        "thesis_attachments", 
        "proposal_form", 
        str(thesis.sy_start)
        )
    
    # create directory for the year
    if not os.path.exists(path):
        os.makedirs(path)
    
    # filename
    path = os.path.join(path, thesis.proposal_form)

    # check kung maooverwrite pag sinave on same file path
    file.save(path)

def remove_proposal_form(thesis):

    path = os.path.join(
        current_app.root_path, 
        "static", 
        "thesis_attachments", 
        "proposal_form", 
        str(thesis.sy_start),
        thesis.proposal_form
        )

    if os.path.exists(path):
        
        os.remove(path)