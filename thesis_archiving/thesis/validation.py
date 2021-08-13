from thesis_archiving.validation import validate_empty
from thesis_archiving.models import User, Program, Category, Group, QuantitativeRating
from marshmallow import Schema, fields, validate, pre_load, post_load, validates, ValidationError
from datetime import datetime
import pytz

class CreateThesisSchema(Schema):
	csrf_token = fields.Str(required=True) # no need for extra validations. handled by flask automatically.
	
	title = fields.Str(required=True, validate=validate.And(
		validate_empty, validate.Length(1,250)
		))
	
	is_old = fields.Bool(required=True)
	
	overview = fields.Str(required=True, validate=validate.And(
		validate_empty, validate.Length(1,10000)
		))
	
	area = fields.Str(required=True, validate=validate.And(
		validate_empty, validate.Length(1,120)
		))
	
	keywords = fields.Str(required=True, validate=validate.And(
		validate_empty, validate.Length(1,250)
		))
	
	sy_start = fields.Int(required=True, validate=validate.Range(min=1, max=datetime.now(tz=pytz.timezone('Asia/Manila')).year))
	
	semester = fields.Int(required=True, validate=validate.Range(min=1, max=2))

	adviser_id = fields.Int(required=True)
	category_id = fields.Int(required=True)
	program_id = fields.Int(required=True)
	proponents = fields.Str(required=True, validate=validate_empty)

	@pre_load
	def strip_fields(self, in_data, **kwargs):
		# dont strip password kasi baka may mag set ng spaces yung first and last lmao
		in_data["title"] = in_data["title"].strip()
		in_data["overview"] = in_data["overview"].strip()
		in_data["area"] = in_data["area"].strip()
		in_data["keywords"] = in_data["keywords"].strip()
		in_data["proponents"] = in_data["proponents"].strip()
		
		return in_data
	
	@validates("adviser_id")
	def validate_adviser_id(self, data):
		if not User.query.filter_by(is_adviser=True, id=data).first():
			raise ValidationError("Adviser does not exist.")
	
	@validates("category_id")
	def validate_category_id(self, data):
		if not Category.query.get(data):
			raise ValidationError("Category does not exist.")

	@validates("program_id")
	def validate_program_id(self, data):
		if not Program.query.get(data):
			raise ValidationError("Program does not exist.")

	@validates("proponents")
	def validate_proponents(self, data):
		err = []
		proponents = data.split(',')
		
		for p in proponents:
			if not User.query.filter_by(username=p).first():
				err.append(f"'{p}' does not exist.")
		
		if len(proponents) > len(set(proponents)):
			err.append("You have duplicate proponents.")

		if err:
			raise ValidationError(err)
	
	@post_load
	def create_data(self, data, **kwargs):
		data['proponents'] = data['proponents'].split(',')
		return data

class UpdateThesisSchema(Schema):
	csrf_token = fields.Str(required=True) # no need for extra validations. handled by flask automatically.
	
	title = fields.Str(required=True, validate=validate.And(
		validate_empty, validate.Length(1,250)
		))
	
	is_old = fields.Bool(required=True)
	
	overview = fields.Str(required=True, validate=validate.And(
		validate_empty, validate.Length(1,10000)
		))
	
	area = fields.Str(required=True, validate=validate.And(
		validate_empty, validate.Length(1,120)
		))
	
	keywords = fields.Str(required=True, validate=validate.And(
		validate_empty, validate.Length(1,250)
		))
	
	sy_start = fields.Int(required=True, validate=validate.Range(min=1, max=datetime.now(tz=pytz.timezone('Asia/Manila')).year))
	
	semester = fields.Int(required=True, validate=validate.Range(min=1, max=2))

	adviser_id = fields.Int(required=True)
	category_id = fields.Int(required=True)
	program_id = fields.Int(required=True)
	group_id = fields.Int()
	quantitative_rating_id = fields.Int()

	@pre_load
	def strip_fields(self, in_data, **kwargs):
		# dont strip password kasi baka may mag set ng spaces yung first and last lmao
		in_data["title"] = in_data["title"].strip()
		in_data["overview"] = in_data["overview"].strip()
		in_data["area"] = in_data["area"].strip()
		in_data["keywords"] = in_data["keywords"].strip()
		
		return in_data

	@validates("group_id")
	def validate_group_id(self, data):
		if not Group.query.get(data):
			raise ValidationError("Panel group is invalid.")

	@validates("quantitative_rating_id")
	def validate_quantitative_rating_id(self, data):
		if not QuantitativeRating.query.get(data):
			raise ValidationError("Quantitative rating is invalid.")