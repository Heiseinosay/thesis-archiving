from marshmallow import Schema, fields, validate, ValidationError, validates

from sqlalchemy import or_

from thesis_archiving.validation import validate_empty
from thesis_archiving.models import Group, Thesis, User

class CreateGroupSchema(Schema):
    csrf_token = fields.Str(required=True) # no need for extra validations. handled by flask automatically.

    number = fields.Int(required=True)

    @validates("number")
    def validate_number(self, data):
        if Group.query.filter_by(number=data).first():
            raise ValidationError("Group number is already being used.")

class UpdateGroupSchema(Schema):
    csrf_token = fields.Str(required=True) # no need for extra validations. handled by flask automatically.

    number = fields.Int(required=True)

    panelist_username = fields.Str(validate=validate.And(validate.Length(1,20)))

    def __init__(self, group_obj, **kwargs):
        self.group = group_obj #set instance variable for current subj
        
        super().__init__(**kwargs) #sends arbitarary arguments to base class

    @validates("number")
    def validate_number(self, data):
        group_ = Group.query.filter_by(number=data).first()
        if group_ and group_ !=self.group:
                raise ValidationError("Group number is already used.")

    @validates("panelist_username")
    def validate_panelist_username(self, data):

        user_ = User.query.filter(or_(User.is_adviser == True, User.is_guest_panelist == True), User.username == data).first() 

        if not user_:
            raise ValidationError("Panelist username is not valid.")
        elif user_ in self.group.panelists:
            raise ValidationError("User is already a member of the panel.")


    # @validates("thesis_id")
    # def validate_thesis_id(self, data):
    #     if not Thesis.query.get(data):
    #         raise ValidationError("Thesis does not exist.")

class UpdateRevisionSchema(Schema):
    csrf_token = fields.Str(required=True) # no need for extra validations. handled by flask automatically.

    comment = fields.Str(validate=validate.And(validate.Length(max=10000)))

    is_final = fields.Bool()
