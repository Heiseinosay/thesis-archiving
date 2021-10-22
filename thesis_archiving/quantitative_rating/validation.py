from thesis_archiving import quantitative_rating
from marshmallow import Schema, fields, validate, ValidationError, validates, validates_schema

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

    max_grade = fields.Int(required=True, validate=validate.Range(min=1))

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

class ManuscriptGradeSchema(Schema):
    csrf_token = fields.Str(required=True) # no need for extra validations. handled by flask automatically.
    
    criteria = fields.List(fields.Str(required=True))

    grades = fields.Dict(keys=fields.Str(), values=fields.Int())
    
    max_grade = fields.Int(Required=True)

    is_final = fields.Bool()

    @validates_schema
    def validate_is_final(self, data, **kwargs):
        
        '''
            Ensures all fields has values when is_final is selected
            to be marked for grading.
        '''

        err = {}
        
        if data.get("is_final"):
            # check if all criteria are filled and within range (1 to max grade)
            for c in data["criteria"]:
                if c not in data["grades"]:
                    err[c] = ["Field cannot be empty."]

        if err:
            raise ValidationError(err)

    @validates_schema
    def validate_grades(self, data, **kwargs):
        
        '''
            Check if grades are within range
        '''
        err = {}
        
        for k, v in data["grades"].items():
            # graded and not within range
            if v and v not in range(1, data["max_grade"] + 1):
                err[k] = ["Grade is not within range."]
        
        # try invoking both the schema errors
        if err:
            raise ValidationError(err)


