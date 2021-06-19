from thesis_archiving import db, login_manager
from sqlalchemy.dialects.mysql import INTEGER, BOOLEAN
from flask_login import UserMixin
from datetime import datetime
import pytz

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(user_id)

class Program(db.Model):
	id = db.Column(INTEGER(unsigned=True), primary_key=True)
	name = db.Column(db.String(20), unique=True, nullable=False)
	code = db.Column(db.String(10), unique=True, nullable=False)

	def __repr__(self):
		return f"[{self.id}] {self.name} - {self.code}"

class Category(db.Model):
	id = db.Column(INTEGER(unsigned=True), primary_key=True)
	name = db.Column(db.String(30), unique=True, nullable=False)
	code = db.Column(db.String(10), unique=True, nullable=False)

	def __repr__(self):
		return f"[{self.id}] {self.name} - {self.code}"

# class Logs(db.Model):
# 	id = db.Column(INTEGER(unsigned=True), primary_key=True)
# 	description = db.Column(db.String(60), unique=True, nullable=False)
# 	date = db.Column(db.DateTime, nullable=False, default=lambda:datetime.now(tz=pytz.timezone('Asia/Manila')))

# 	def __repr__(self):
# 		return f"[{self.id}] {self.description} - {self.date}"

class User(db.Model, UserMixin):
	id = db.Column(INTEGER(unsigned=True), primary_key=True)
	username = db.Column(db.String(20), unique=True, nullable=False)
	full_name = db.Column(db.String(64), nullable=False)
	email = db.Column(db.String(64), unique=True)
	password = db.Column(db.String(60), nullable=False)
	is_adviser = db.Column(BOOLEAN(), default=False)
	is_admin = db.Column(BOOLEAN(), default=False)
	is_superuser = db.Column(BOOLEAN(), default=False)
	date_registered = db.Column(db.DateTime, nullable=False, default=lambda:datetime.now(tz=pytz.timezone('Asia/Manila')))

	def __repr__(self):
		return f"[{self.id}] {self.username} - {self.email}"

# class Thesis(db.Model):
# 	id = db.Column(INTEGER(unsigned=True), primary_key=True)
# 	title = db.Column(db.String(250), unique=True, nullable=False)
# 	sy_start = db.Column(db.Integer)
# 	sem = db.Column(db.Integer)
# 	number = db.Column(db.Integer)
# 	area = db.Column(db.String(120))
# 	program_id
# 	adviser_id
# 	proponents_id
# 	overview = db.Column(db.String(500))
# 	keywords = db.Column(db.String(120))
# 	category_id
# 	date_deployed = db.Column(db.DateTime)
# 	date_registered = db.Column(db.DateTime, nullable=False, default=lambda:datetime.now(tz=pytz.timezone('Asia/Manila')))
# 	is_old = db.Column(BOOLEAN(), default=False)

# 	def __repr__(self):
# 		return f"[{self.id}] {self.title[0: 20 if len(self.title) > 20 else len(self.title)]}{ '...' if len(self.title) > 20 else '' }"
	
	# @staticmethod
	# def thesis_number():
	# 	'''
	# 		Get the number of latest new thesis

	# 		(old theses are those written before the start of this system's development)
	# 	'''

	# 	thesis = Thesis.query.filter_by(is_old=False).order_by(Thesis.date_registered.desc()).first()
		
	# 	return thesis.number + 1 if thesis else 1 
