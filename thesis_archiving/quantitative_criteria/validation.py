from thesis_archiving.validation import validate_empty
from thesis_archiving.models import QuantitativeRating, QuantitativeCriteria
from marshmallow import Schema, fields, validate, pre_load, validates, ValidationError, validates_schema



class UpdateQuantitativeCriteria(Schema):
    csrf_token = fields.Str(required=True) # no need for extra validations. handled by flask automatically.

    name = fields.Str(required=True, validate=validate.And(validate_empty, validate.Length(1,64)))

    description = fields.Str(validate=validate.And(validate_empty, validate.Length(1,500)))

    rating_rate = fields.Int(validate=validate.Range(min=1))

    rating_description = fields.Str(validate=validate.And(validate_empty, validate.Length(1,500)))

    def __init__(self, quantitative_criteria_obj, max_grade, **kwargs):
        self.quantitative_criteria = quantitative_criteria_obj
        self.max_grade = max_grade #set instance variable for current quanti rating
        
        super().__init__(**kwargs)

    @validates("rating_rate")
    def validate_rate(self, data):
        if data > self.max_grade:
            raise ValidationError(f"Rating cannot be greater than maximum grade ({self.max_grade}).")

        if self.quantitative_criteria.ratings.filter_by(rate=data).first():
            raise ValidationError("Rating already exist.")