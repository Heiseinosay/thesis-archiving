import pandas as pd
from io import BytesIO
from datetime import datetime
import pytz
from flask_login import current_user
from flask import flash, abort
from functools import wraps

from thesis_archiving import db
from thesis_archiving.models import QuantitativePanelistGrade, QuantitativeCriteriaGrade, QuantitativeCriteria

def export_to_excel(file_prefix, data, columns):

    # https://pandas.pydata.org/pandas-docs/stable/user_guide/io.html#writing-excel-files-to-memory

    # https://pandas.pydata.org/pandas-docs/stable/reference/api/pandas.DataFrame.to_excel.html#

    # binary object
    output = BytesIO()

    # excel writer
    writer = pd.ExcelWriter(output, engine="openpyxl")

    df = pd.DataFrame(data, columns=columns)

    # write data to binary object
    df.to_excel(writer, index=False)
    writer.save()

    # seek pointer to beginning of the object to return the whole content
    output.seek(0)
    
    # file name
    date = datetime.now(tz=pytz.timezone('Asia/Manila')).strftime("%Y-%m-%d")
    download_name = file_prefix + date + ".xlsx"

    return output, download_name

def has_roles(*roles):
    def decorator(original_route):
        @wraps(original_route) #wraps is for preserving functions passed
        def wrapped_function(*args, **kwargs):
            
            permitted = False

            # not logged in
            if not current_user.is_authenticated:
                abort(401)

            if "is_adviser" in roles and current_user.is_adviser:
                permitted = True
            
            if "is_guest_panelist" in roles and current_user.is_guest_panelist:
                permitted = True

            if "is_admin" in roles and current_user.is_admin:
                permitted = True
            
            # hindi na needed "is_superuser" arg
            # pero nilalagay nalang for uniformity
            if current_user.is_superuser:
                permitted = True

            if permitted:
                return original_route(*args,**kwargs)

            # return forbidden 
            abort(403)

        return wrapped_function

    return decorator


def get_quantitative_panelist_grade(quantitative_rating_id, thesis_id, panelist_id=None):
    '''
        Returns a query object for the thesis's quantitative panelist grades
    
    '''
    query = QuantitativePanelistGrade.query.filter(
            # get the panelist grade id who graded those criteria
            QuantitativePanelistGrade.id.in_(
                db.session.query(QuantitativeCriteriaGrade.quantitative_panelist_grade_id).where(
                    # get id of grades pointing to those criteria
                    QuantitativeCriteriaGrade.quantitative_criteria_id.in_(
                        # obtain all id ng MANUSCRIPT rating criteria ng thesis
                        db.session.query(QuantitativeCriteria.id).where(QuantitativeCriteria.quantitative_rating_id == quantitative_rating_id)        
                    )
                )
            ),
            QuantitativePanelistGrade.thesis_id == thesis_id
        )

    if panelist_id:
        query.filter_by(panelist_id=panelist_id)
    
    return query