from flask import current_app
from flask_login import UserMixin
from sqlalchemy.dialects.mysql import INTEGER, BOOLEAN, BIGINT

from thesis_archiving import db, login_manager

from datetime import datetime
import pytz
from itsdangerous import TimedJSONWebSignatureSerializer as Serializer

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(user_id)


'''
	syntax i followed for creating models w/ relationships

	one to many

	class Parent():
		...

		children = db.relationship()
		
	class Child():
		...

		parent_id = db.Column()

'''

class Program(db.Model):
	id = db.Column(INTEGER(unsigned=True), primary_key=True)
	name = db.Column(db.String(20), unique=True, nullable=False)
	code = db.Column(db.String(10), unique=True, nullable=False)

	theses = db.relationship('Thesis', backref='program', lazy='dynamic')

	def __repr__(self):
		return f"[{self.id}] {self.name} - {self.code}"

class Category(db.Model):
	id = db.Column(INTEGER(unsigned=True), primary_key=True)
	name = db.Column(db.String(30), unique=True, nullable=False)
	code = db.Column(db.String(10), unique=True, nullable=False)

	theses = db.relationship('Thesis', backref='category', lazy='dynamic')

	def __repr__(self):
		return f"[{self.id}] {self.name} - {self.code}"

# user to thesis many to many helper table
proponents = db.Table('proponents', 
	db.Column('user_id', INTEGER(unsigned=True), db.ForeignKey('user.id')),
	db.Column('thesis_id', INTEGER(unsigned=True), db.ForeignKey('thesis.id'))
)

class User(db.Model, UserMixin):
	id = db.Column(INTEGER(unsigned=True), primary_key=True)
	username = db.Column(db.String(20), unique=True, nullable=False)
	full_name = db.Column(db.String(64), nullable=False)
	email = db.Column(db.String(64), unique=True)
	password = db.Column(db.String(60), nullable=False)
	is_student = db.Column(BOOLEAN(), default=False)
	is_adviser = db.Column(BOOLEAN(), default=False)
	is_admin = db.Column(BOOLEAN(), default=False)
	is_superuser = db.Column(BOOLEAN(), default=False)
	date_registered = db.Column(db.DateTime, nullable=False, default=lambda:datetime.now(tz=pytz.timezone('Asia/Manila')))

	# cascade delete
	logs = db.relationship('Log', backref='user', lazy='dynamic', cascade="all, delete") 
	
	advisees = db.relationship('Thesis', backref='adviser', lazy='dynamic')

	def __repr__(self):
		return f"[{self.id}] {self.username} - {self.full_name}"

	def get_reset_token(self, expires_sec=259200):
		# 3 days expiration
		s = Serializer(current_app.config['SECRET_KEY'], expires_sec)
		return s.dumps({'user_id':self.id}).decode('utf-8')

	@staticmethod
	def verify_reset_token(token):
		s = Serializer(current_app.config['SECRET_KEY'])

		try:
			_user_id = s.loads(token)['user_id']
		except:
			return None

		return User.query.get(_user_id)

class Log(db.Model):
	id = db.Column(BIGINT(unsigned=True), primary_key=True)
	description = db.Column(db.String(60), nullable=False)
	date = db.Column(db.DateTime, nullable=False, default=lambda:datetime.now(tz=pytz.timezone('Asia/Manila')))

	user_id = db.Column(INTEGER(unsigned=True), db.ForeignKey('user.id'), nullable=False)

	def __repr__(self):
		return f"[{self.id}] {self.description} - {self.date}"


class Thesis(db.Model):
	id = db.Column(INTEGER(unsigned=True), primary_key=True)
	title = db.Column(db.String(250), nullable=False)
	is_old = db.Column(BOOLEAN(), nullable=False, default=False)
	overview = db.Column(db.String(10000))
	area = db.Column(db.String(120))
	keywords = db.Column(db.String(250))
	sy_start = db.Column(db.Integer)
	semester = db.Column(db.Integer)
	number = db.Column(db.Integer, unique=True)
	date_deployed = db.Column(db.DateTime)
	date_registered = db.Column(db.DateTime, nullable=False, default=lambda:datetime.now(tz=pytz.timezone('Asia/Manila')))

	adviser_id = db.Column(INTEGER(unsigned=True), db.ForeignKey('user.id'), nullable=False)
	category_id = db.Column(INTEGER(unsigned=True), db.ForeignKey('category.id'), nullable=False)
	program_id = db.Column(INTEGER(unsigned=True), db.ForeignKey('program.id'), nullable=False)
	proponents = db.relationship('User', secondary=proponents, lazy='dynamic', backref=db.backref('theses', lazy='dynamic'))

	def __repr__(self):
		title = self.title[0: (50 if len(self.title) > 50 else len(self.title))] + ('...' if len(self.title) > 50 else '')
		old_or_number = "old" if self.is_old else f"{self.sy_start}-{self.semester}-{self.category.code}{self.program.code}-{self.number}"

		return f"[{self.id}] {old_or_number} {title}"
	
	@staticmethod
	def thesis_number():
		'''
			Get the number of latest NEW thesis

			notes:
				OLD theses are those written before the start of this system's development

				important yung id sorting dahil nadedefault na ascending maski descending yung ibang column

				finilter yung is_old=False kasi baka may ma add na number sa hindi naman old
		'''

		# thesis = Thesis.query.filter_by(is_old=False).filter(Thesis.number.isnot(None)).order_by(Thesis.date_registered.desc()).order_by(Thesis.id.desc()).order_by(Thesis.number.desc()).first()
		thesis = Thesis.query.filter_by(is_old=False).filter(Thesis.number.isnot(None)).order_by(Thesis.number.desc()).first()

		return thesis.number + 1 if (thesis and thesis.number) else 1 
