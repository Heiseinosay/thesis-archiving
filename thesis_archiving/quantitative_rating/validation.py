from marshmallow import Schema, fields, validate, ValidationError, validates

from thesis_archiving.validation import validate_empty
from thesis_archiving.models import QuantitativeRating

class CreateQuantitativeRatingSchema(Schema):
    csrf_token = fields.Str(required=True) # no need for extra validations. handled by flask automatically.

    name = fields.Str(required=True, validate=validate.And(validate_empty, validate.Length(1,120)))

    @validates("name")
    def validate_name(self, data):
        if QuantitativeRating.query.filter_by(name=data).first():
            raise ValidationError("Name is already being used.")