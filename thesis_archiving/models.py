from flask import current_app, abort
from flask.helpers import flash
from flask_login import UserMixin
from sqlalchemy.dialects.mysql import INTEGER, BOOLEAN, BIGINT
from sqlalchemy import and_

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

# groups to user many to many helper table
panelists = db.Table('panelists', 
	db.Column('group_id', INTEGER(unsigned=True), db.ForeignKey('group.id')),
	db.Column('user_id', INTEGER(unsigned=True), db.ForeignKey('user.id'))
)

class User(db.Model, UserMixin):

	# ambiguous foreign keys fix
	# https://www.reddit.com/r/flask/comments/2o4ejl/af_flask_sqlalchemy_two_foreign_keys_referencing/

	id = db.Column(INTEGER(unsigned=True), primary_key=True)
	username = db.Column(db.String(20), unique=True, nullable=False)
	full_name = db.Column(db.String(64), nullable=False)
	email = db.Column(db.String(64), unique=True)
	password = db.Column(db.String(60), nullable=False)
	is_student = db.Column(BOOLEAN(), default=False, nullable=False)
	is_adviser = db.Column(BOOLEAN(), default=False, nullable=False)
	is_guest_panelist = db.Column(BOOLEAN(), default=False, nullable=False)
	is_admin = db.Column(BOOLEAN(), default=False, nullable=False)
	is_superuser = db.Column(BOOLEAN(), default=False, nullable=False)
	date_registered = db.Column(db.DateTime, nullable=False, default=lambda:datetime.now(tz=pytz.timezone('Asia/Manila')))

	# cascade delete
	logs = db.relationship('Log', backref='user', lazy='dynamic', cascade="all, delete") 
	
	advisees = db.relationship('Thesis', backref='adviser', lazy='dynamic')

	group_chairman = db.relationship('Group', backref='chairman', lazy='dynamic')

	quantitative_panelist_grades = db.relationship('QuantitativePanelistGrade', backref='panelist', lazy='dynamic', cascade="all, delete")

	student_individual_ratings = db.relationship('IndividualRating', backref='student', lazy='dynamic', foreign_keys='IndividualRating.student_id', cascade="all, delete")

	panelist_individual_rating = db.relationship('IndividualRating', backref='panelist', lazy='dynamic', foreign_keys='IndividualRating.panelist_id', cascade="all, delete")

	revision_list = db.relationship('RevisionList', backref='panelist', lazy='dynamic', cascade="all, delete")

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

	def check_quantitative_panelist_grade(self, thesis, quantitative_rating):

		# fetch the panel's quantatitative grades for the thesis
		# panelist_grade = self.quantitative_panelist_grades.filter_by(thesis_id=thesis.id).first()

		panelist_grade = db.session.query(QuantitativePanelistGrade).where(
			and_(
					# get the panelist id who graded those criteria
					QuantitativePanelistGrade.id.in_(
						db.session.query(QuantitativeCriteriaGrade.quantitative_panelist_grade_id).where(
							# get id of grades pointing to those criteria
							QuantitativeCriteriaGrade.quantitative_criteria_id.in_(
								# obtain all id ng MANUSCRIPT rating criteria ng thesis
								db.session.query(QuantitativeCriteria.id).where(QuantitativeCriteria.quantitative_rating_id == quantitative_rating.id)        
							)
						)
					),
					QuantitativePanelistGrade.thesis_id == thesis.id,
					QuantitativePanelistGrade.panelist_id == self.id
				)
			).first()

		# create if there is none
		if not panelist_grade:
			
			# create panelist grade for the thesis
			panelist_grade = QuantitativePanelistGrade()
			panelist_grade.panelist_id = self.id
			panelist_grade.thesis_id = thesis.id
			
			# fetch each criteria of the rating for the thesis
			# might raise an error if the thesis HAS NO quantitative grading criteria selected
			criteria = quantitative_rating.criteria

			# create grade for each criteria
			for criterion in criteria:
				# grade object
				grade = QuantitativeCriteriaGrade()
				
				# set quantitative_criteria_id for the grade object
				criterion.grades.append(grade)

				# set quantitative_panelist_grade_id for the grade object
				panelist_grade.grades.append(grade)
			
			# insert newly created panelist_grade for the thesis
			try:
				db.session.add(panelist_grade)
				db.session.commit()
				flash('Created quantitative rating grades.','success')
			except:
				flash('An error occured while creating quantitative rating grades.','danger')

	def check_student_individual_rating(self, student, thesis_id, panelist_id):
		'''
			return individual rating
		'''
		# check for existing rating for the thesis and corresponding student
		rating = student.student_individual_ratings.filter_by(
			thesis_id = thesis_id,
			panelist_id = panelist_id
		).first()
		
		# create a rating if there is none
		if not rating:
			rating = IndividualRating()
			rating.student_id = student.id
			rating.thesis_id = thesis_id
			rating.panelist_id = panelist_id

			try:
				db.session.add(rating)
				db.session.commit()
			except:
				abort(500)
				
		return rating


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
	date_defense = db.Column(db.DateTime)
	qualitative_rating = db.Column(db.String(64))
	proposal_form = db.Column(db.String(250), unique=True) 
	date_registered = db.Column(db.DateTime, nullable=False, default=lambda:datetime.now(tz=pytz.timezone('Asia/Manila')))

	adviser_id = db.Column(INTEGER(unsigned=True), db.ForeignKey('user.id'), nullable=False)
	category_id = db.Column(INTEGER(unsigned=True), db.ForeignKey('category.id'), nullable=False)
	
	group_id = db.Column(INTEGER(unsigned=True), db.ForeignKey('group.id'))
	presentor_number = db.Column(db.Integer)
	
	program_id = db.Column(INTEGER(unsigned=True), db.ForeignKey('program.id'), nullable=False)
	proponents = db.relationship('User', secondary=proponents, lazy='dynamic', backref=db.backref('theses', lazy='dynamic'))

	# manuscript selection
	quantitative_rating_id = db.Column(INTEGER(unsigned=True), db.ForeignKey('quantitative_rating.id'))

	# developed thesis project
	quantitative_rating_developed_id = db.Column(INTEGER(unsigned=True), db.ForeignKey('quantitative_rating.id'))

	quantitative_panelist_grades = db.relationship('QuantitativePanelistGrade', backref='thesis', lazy='dynamic', cascade="all, delete")

	individual_rating_panelist_grades = db.relationship('IndividualRating', backref='thesis', lazy='dynamic', cascade="all, delete")


	revision_lists = db.relationship('RevisionList', backref='thesis', lazy='dynamic', cascade="all, delete")

	def __repr__(self):
		title = self.title[0: (50 if len(self.title) > 50 else len(self.title))] + ('...' if len(self.title) > 50 else '')
		old_or_number = "old" if self.is_old else f"{self.sy_start}-{self.semester}-{self.category.code}{self.program.code}-{self.number}"

		return f"[{self.id}] {old_or_number} {title}"
	
	def call_number(self):
		return f"{self.sy_start}-{self.semester}-{self.category.code}{self.program.code}-{self.number}"

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
	
	def check_revision_lists(self, user):
		'''
			Returns revision list for the panel.

			If none, create one
		'''

		revision = self.revision_lists.filter_by(panelist_id=user.id).first()
		
		if not revision:
			revision = RevisionList()
			revision.thesis_id = self.id
			revision.panelist_id = user.id

			try:
				db.session.add(revision)
				db.session.commit()
				flash("Successfully created new revision.","success")
			except:
				flash("An error occured.","danger")

		return revision

class Group(db.Model):
	id = db.Column(INTEGER(unsigned=True), primary_key=True)
	number = db.Column(db.Integer, unique=True, nullable=False)
	chairmain_id = db.Column(INTEGER(unsigned=True), db.ForeignKey('user.id'))
	
	# adviser users
	panelists = db.relationship('User', secondary=panelists, lazy='dynamic', backref=db.backref('groups', lazy='dynamic'))
	# theses
	presentors = db.relationship('Thesis', backref='group', lazy='dynamic') 
	
	# presentor ids cannot be the same 
	# can only be chairman if a panelist
	# presentors = thesis.presentors.sortby presentor number
	# for i in range(group presentors length sort by presentor number):
	# 	presentors[i].number = i + 1

# =================================================
# A thesis can have 1 QuantitativeRating template it can follow (depending sa college) 
# wherein its criteria can be dynamically set through QuantitativeCriteria

# A panelist will have a collection of its grades for a certain thesis stored in QuantitativePanelGrade
# the QuantitatveGrades stored in it will have the corresponding grade and the QunatitativeCriteria it grades
# it can also be marked by is_final to know if the panelist is done grading the quantitative aspect for that specfic thesis

# quanti rating is also panel specific for each thesis
# =================================================

class QuantitativeRating(db.Model):
	id = db.Column(INTEGER(unsigned=True), primary_key=True)
	name = db.Column(db.String(120), unique=True)
	max_grade = db.Column(db.Integer, default=5)

	# theses using this rating template for MANUSCRIPT
	theses = db.relationship('Thesis', backref='manuscript_rating', lazy='dynamic', foreign_keys='Thesis.quantitative_rating_id')

	# theses using this rating template for DEVELOPED THESIS PROJECT
	developed_theses = db.relationship('Thesis', backref='developed_thesis_rating', lazy='dynamic', foreign_keys='Thesis.quantitative_rating_developed_id')

	# adding new criteria will not reflect on ongoing gradings
	criteria = db.relationship('QuantitativeCriteria', backref='rating', lazy='dynamic', cascade="all, delete")

class QuantitativeCriteria(db.Model):
	id = db.Column(INTEGER(unsigned=True), primary_key=True)
	name =  db.Column(db.String(64), nullable=False)
	description =  db.Column(db.String(500))
	quantitative_rating_id = db.Column(INTEGER(unsigned=True), db.ForeignKey('quantitative_rating.id', ondelete='cascade'), nullable=False)

	grades = db.relationship('QuantitativeCriteriaGrade', backref='criteria', lazy='dynamic', cascade="all, delete")

	ratings = db.relationship('QuantitativeCriteriaRating', backref='criteria', lazy='dynamic', cascade="all, delete")

class QuantitativeCriteriaRating(db.Model):
	id = db.Column(INTEGER(unsigned=True), primary_key=True)
	rate = db.Column(INTEGER(unsigned=True), nullable=False)
	description =  db.Column(db.String(500))
	quantitative_criteria_id = db.Column(INTEGER(unsigned=True), db.ForeignKey('quantitative_criteria.id', ondelete='cascade'), nullable=False)

# collection of grades a panel has
class QuantitativePanelistGrade(db.Model):
	id = db.Column(INTEGER(unsigned=True), primary_key=True)
	is_final = db.Column(BOOLEAN(), default=False, nullable=False)
	panelist_id = db.Column(INTEGER(unsigned=True), db.ForeignKey('user.id', ondelete='cascade'), nullable=False)
	thesis_id = db.Column(INTEGER(unsigned=True), db.ForeignKey('thesis.id', ondelete='cascade'), nullable=False)

	grades = db.relationship('QuantitativeCriteriaGrade', backref='panelist_grade', lazy='dynamic', cascade="all, delete")

class QuantitativeCriteriaGrade(db.Model):
	id = db.Column(INTEGER(unsigned=True), primary_key=True)
	grade = db.Column(db.Integer)
	quantitative_criteria_id = db.Column(INTEGER(unsigned=True), db.ForeignKey('quantitative_criteria.id', ondelete='cascade'), nullable=False)
	quantitative_panelist_grade_id = db.Column(INTEGER(unsigned=True), db.ForeignKey('quantitative_panelist_grade.id', ondelete='cascade'), nullable=False)

# =================================================
# individual rating is panel specific for each student
# =================================================
class IndividualRating(db.Model):
	id = db.Column(INTEGER(unsigned=True), primary_key=True)
	intelligent_response = db.Column(db.Integer)
	respectful_response = db.Column(db.Integer)
	communication_skills = db.Column(db.Integer)
	confidence = db.Column(db.Integer)
	attire = db.Column(db.Integer)
	is_final = db.Column(BOOLEAN(), default=False, nullable=False)

	student_id = db.Column(INTEGER(unsigned=True), db.ForeignKey('user.id', ondelete='cascade'), nullable=False)
	thesis_id = db.Column(INTEGER(unsigned=True), db.ForeignKey('thesis.id', ondelete='cascade'), nullable=False)
	panelist_id = db.Column(INTEGER(unsigned=True), db.ForeignKey('user.id', ondelete='cascade'), nullable=False)

	def check_thesis_id(self, thesis_id):
		return True if thesis_id == self.thesis.id else False
			

# =================================================
# revision list is panel specific for each student
# =================================================
class RevisionList(db.Model):
	id = db.Column(INTEGER(unsigned=True), primary_key=True)
	comment = db.Column(db.String(10000))
	is_final = db.Column(BOOLEAN(), default=False, nullable=False)

	thesis_id = db.Column(INTEGER(unsigned=True), db.ForeignKey('thesis.id'), nullable=False)
	panelist_id = db.Column(INTEGER(unsigned=True), db.ForeignKey('user.id'), nullable=False)