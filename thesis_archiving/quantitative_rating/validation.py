from thesis_archiving import quantitative_rating
from marshmallow import Schema, fields, validate, ValidationError, validates

from thesis_archiving.validation import validate_empty
from thesis_archiving.models import QuantitativeCriteria, QuantitativeRating

class CreateQuantitativeRatingSchema(Schema):
    csrf_token = fields.Str(required=True) # no need for extra validations. handled by flask automatically.

    name = fields.Str(required=True, validate=validate.And(validate_empty, validate.Length(1,120)))

    @validates("name")
    def validate_name(self, data):
        if QuantitativeRating.query.filter_by(name=data).first():
            raise ValidationError("Name is already being used.")

class UpdateQuantitativeRatingSchema(Schema):
    csrf_token = fields.Str(required=True) # no need for extra validations. handled by flask automatically.

    name = fields.Str(required=True, validate=validate.And(validate_empty, validate.Length(1,120)))

    criteria_name = fields.Str(validate=validate.And(validate.Length(1,64)))

    def __init__(self, quantitative_rating_obj, **kwargs):
        self.quantitative_rating = quantitative_rating_obj #set instance variable for current quanti rating
        
        super().__init__(**kwargs) #sends arbitarary arguments to base class


    @validates("name")
    def validate_name(self, data):
        
        quantitative_rating_ = QuantitativeRating.query.filter_by(name=data).first()

        if quantitative_rating_ and quantitative_rating_ != self.quantitative_rating:
            raise ValidationError("Name is already being used.")

    @validates("criteria_name")
    def validate_criteria_name(self, data):

        # find if the current criteria name is already in the rating's set of criteria
        quantitative_criteria_ = self.quantitative_rating.criteria.filter_by(name=data).first()

        if quantitative_criteria_:
            raise ValidationError("Criteria already exist.")