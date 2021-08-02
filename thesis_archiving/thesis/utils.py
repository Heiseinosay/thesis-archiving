from thesis_archiving.models import User, Program, Category, Group
from datetime import datetime
import pytz

def select_choices():

    _choices = {
        'adviser_id' : {adviser.id : adviser.full_name for adviser in User.query.filter_by(is_adviser=True).order_by(User.full_name).all()},
        'program_id' : {program.id : program.name for program in Program.query.order_by(Program.name).all()},
        'category_id' : {category.id : category.name for category in Category.query.order_by(Category.name).all()},
        'sy_start' : { year : year for year in range(2000, datetime.now(tz=pytz.timezone('Asia/Manila')).year + 1)},
        'semester' : {1:1, 2:2},
        'is_old' : {1:'Old', 0:'New'},
        'group_id': { group.id:group.number for group in Group.query.order_by(Group.number).all() }
    }

    return _choices