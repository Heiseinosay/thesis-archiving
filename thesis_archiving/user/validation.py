from marshmallow import Schema, fields, validates, ValidationError, validate, validates_schema 

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
    username = fields.Str(required=True, validate=validate_empty)
    password = fields.Str(required=True, validate=validate_empty)

    @validates_schema
    def validate_user(self, data, **kwargs):

        # check user encrypted password
        if not(data["username"] and data["password"]):
            raise ValidationError("User credentials does not match or exist.")