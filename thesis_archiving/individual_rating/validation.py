from marshmallow import Schema, fields, validate, ValidationError, validates_schema

class IndividualRatingSchema(Schema):
    csrf_token = fields.Str(required=True) # no need for extra validations. handled by flask automatically.

    intelligent_response = fields.Int(validate=validate.Range(min=1, max=6))
    
    respectful_response = fields.Int(validate=validate.Range(min=1, max=6))
    
    communication_skills = fields.Int(validate=validate.Range(min=1, max=6))
    
    confidence = fields.Int(validate=validate.Range(min=1, max=6))
    
    attire = fields.Int(validate=validate.Range(min=1, max=6))
    
    is_final = fields.Bool()

    @validates_schema
    def validate_is_final(self, data, **kwargs):
        
        '''
            Ensures all fields has values when is_final is selected
            to be marked for grading.
        '''

        err = {}
        
        if data.get("is_final"):

            if not data.get("intelligent_response"):
                err["intelligent_response"] = ["Field cannot be empty."]
            
            if not data.get("respectful_response"):
                err["respectful_response"] = ["Field cannot be empty."]

            if not data.get("communication_skills"):
                err["communication_skills"] = ["Field cannot be empty."]

            if not data.get("confidence"):
                err["confidence"] = ["Field cannot be empty."]

            if not data.get("attire"):
                err["attire"] = ["Field cannot be empty."]

        if err:
            raise ValidationError(err)
