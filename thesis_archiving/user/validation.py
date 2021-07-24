from marshmallow import Schema, fields, validate, pre_load, validates_schema, ValidationError, validates
from thesis_archiving.validation import validate_empty
from thesis_archiving.models import User

class LoginSchema(Schema):
    csrf_token = fields.Str(required=True) # no need for extra validations. handled by flask automatically.
    username = fields.Str(required=True, validate=validate_empty)
    password = fields.Str(required=True, validate=validate_empty)
    # file = fields.Raw(required=True)

    @pre_load
    def strip_fields(self, in_data, **kwargs):
        # dont strip password kasi baka may mag set ng spaces yung first and last lmao
        in_data["username"] = in_data["username"].strip()

        return in_data

class PasswordResetSchema(Schema):
    csrf_token = fields.Str(required=True) # no need for extra validations. handled by flask automatically.

    password = fields.Str(required=True, validate=validate.And(
    validate_empty, validate.Length(max=60)
    ))

    confirm_password = fields.Str(required=True, validate=validate.And(
    validate_empty, validate.Length(max=60)
    ))

    @validates_schema
    def validate_confirm_password(self, data, **kwargs):
        err = {}
        if data["password"] != data["confirm_password"]:
            err["confirm_password"] = ["Password do not match."]
        
        if err:
            raise ValidationError(err)
    
class PasswordResetRequestSchema(Schema):
    csrf_token = fields.Str(required=True) # no need for extra validations. handled by flask automatically.

    email = fields.Email(validate=validate.And(
    validate_empty, validate.Length(max=64)
    ))

    @pre_load
    def strip_fields(self, in_data, **kwargs):
        # dont strip password kasi baka may mag set ng spaces yung first and last lmao
        in_data["email"] = in_data["email"].strip()

        return in_data

    @validates("email")
    def validate_email(self, data):
        if not User.query.filter_by(email=data).first():
            raise ValidationError("Email does not exist.")


class CreateUserSchema(Schema):
    csrf_token = fields.Str(required=True) # no need for extra validations. handled by flask automatically.
    username = fields.Str(required=True, validate=validate.And(
    validate_empty, validate.Length(max=20)
    ))

    full_name = fields.Str(required=True, validate=validate.And(
    validate_empty, validate.Length(max=64)
    ))

    email = fields.Email(validate=validate.And(
    validate_empty, validate.Length(max=64)
    ))

    password = fields.Str(required=True, validate=validate.And(
    validate_empty, validate.Length(max=60)
    ))

    confirm_password = fields.Str(required=True, validate=validate.And(
    validate_empty, validate.Length(max=60)
    ))

    is_student = fields.Bool(missing=False)
    is_adviser = fields.Bool(missing=False)
    is_admin = fields.Bool(missing=False)
    is_superuser = fields.Bool(missing=False)

    @pre_load
    def strip_fields(self, in_data, **kwargs):
        # dont strip password kasi baka may mag set ng spaces yung first and last lmao
        in_data["username"] = in_data["username"].strip()
        in_data["full_name"] = in_data["full_name"].strip()
        in_data["email"] = in_data["email"].strip()

        return in_data
    
    @validates("username")
    def validate_username(self, data):
        if User.query.filter_by(username=data).first():
            raise ValidationError("Username is taken.")

    @validates("email")
    def validate_email(self, data):
        if User.query.filter_by(email=data).first():
            raise ValidationError("Email is taken.")

    @validates_schema
    def validate_confirm_password(self, data, **kwargs):
        err = {}
        if data["password"] != data["confirm_password"]:
            err["confirm_password"] = ["Password do not match."]
        
        if err:
            raise ValidationError(err)

class UpdateUserSchema(Schema):
    csrf_token = fields.Str(required=True) # no need for extra validations. handled by flask automatically.
    username = fields.Str(required=True, validate=validate.And(
    validate_empty, validate.Length(max=20)
    ))

    full_name = fields.Str(required=True, validate=validate.And(
    validate_empty, validate.Length(max=64)
    ))

    email = fields.Email(validate=validate.And(
    validate_empty, validate.Length(max=64)
    ))

    is_adviser = fields.Bool(missing=False)
    is_admin = fields.Bool(missing=False)
    is_superuser = fields.Bool(missing=False)
    
    def __init__(self, user_obj, **kwargs):
        self.user = user_obj #set instance variable for current subj
        
        super().__init__(**kwargs) #sends arbitarary arguments to base class

    @pre_load
    def strip_fields(self, in_data, **kwargs):
        # dont strip password kasi baka may mag set ng spaces yung first and last lmao
        in_data["username"] = in_data["username"].strip()
        in_data["full_name"] = in_data["full_name"].strip()
        in_data["email"] = in_data["email"].strip()

        return in_data
    
    @validates("username")
    def validate_username(self, data):
        _user = User.query.filter_by(username=data).first()
        if _user and _user != self.user:
            raise ValidationError("Username is taken.")

    @validates("email")
    def validate_email(self, data):
        _user = User.query.filter_by(email=data).first()
        if _user and _user != self.user:
            raise ValidationError("Email is taken.")
