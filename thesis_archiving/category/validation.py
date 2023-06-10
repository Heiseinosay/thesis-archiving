from marshmallow import Schema, fields, validate, pre_load, ValidationError, validates
from thesis_archiving.validation import validate_empty
from thesis_archiving.models import Category

class CreateCategorySchema(Schema):
    csrf_token = fields.Str(required=True) # no need for extra validations. handled by flask automatically.
    name = fields.Str(required=True, validate=validate.And(
    validate_empty, validate.Length(max=30)
    ))

    code = fields.Str(required=True, validate=validate.And(
    validate_empty, validate.Length(max=10)
    ))

    @pre_load
    def strip_fields(self, in_data, **kwargs):
        # dont strip password kasi baka may mag set ng spaces yung first and last lmao
        in_data["name"] = in_data["name"].strip()
        in_data["code"] = in_data["code"].strip()

        return in_data
    
    @validates("name")
    def validate_name(self, data):
        if Category.query.filter_by(name=data).first():
            raise ValidationError("Name is taken.")

    @validates("code")
    def validate_code(self, data):
        if Category.query.filter_by(code=data).first():
            raise ValidationError("Code is taken.")