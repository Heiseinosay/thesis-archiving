from flask import current_app
from marshmallow import Schema, fields, validates, ValidationError, validate, validates_schema 
import os

def validate_empty(data):
    if len(data.strip()) == 0:
        raise ValidationError("Field cannot be empty.")

def validate_input(data, schema):
    '''
        can only take single dictionary of data
    '''

    result = {
        'valid' : {},
        'invalid' : {}
    }

    try:
        result['valid'] = schema().load(data)

    except ValidationError as err:
        result['invalid'] = err.messages

    return result

class LoginSchema(Schema):
    csrf_token = fields.Str(required=True) # no need for extra validations. handled by flask automatically.
    username = fields.Str(required=True, validate=validate_empty)
    password = fields.Str(required=True, validate=validate_empty)
    # file = fields.Raw(required=True)

    # @validates("file")
    # def testfile(self, data):
        
    #     err = []
    #     valid_ext = ['pdf','docx','doc']

    #     # file size in mb
    #     size = len(data.read()) / 1024 / 1024

        
    #     if size > 5:
    #         err.append("File is greater than 5 mb.")

    #     if data extension not in valid_ext:
    #         err.append("File type not allowed.")
        
    #     if err:
    #         raise ValidationError(err)

    #     # return cursor beginning of file
    #     # it may be possible na tanggalin tong part na to dito? and ilipat ang saving logic elsewhere?
    #     data.seek(0)
    #     data.save(os.path.join(current_app.root_path,'path','to','file','filename.ext'))

    @validates_schema
    def validate_user(self, data, **kwargs):

        # check user encrypted password
        if not(data["username"] and data["password"]):
            raise ValidationError("User credentials does not match or exist.")