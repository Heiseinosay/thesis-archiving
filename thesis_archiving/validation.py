from marshmallow import ValidationError

def validate_input(data, schema, **kwargs):
    '''
        can only take single dictionary of data
    '''

    result = {
        'valid' : {},
        'invalid' : {}
    }
    
    try:
        result['valid'] = schema(**kwargs).load(data)

    except ValidationError as err:
        result['valid'] = err.valid_data
        result['invalid'] = err.messages

    return result

def validate_empty(data):
    if len(data) == 0:
        raise ValidationError("Field cannot be empty.")

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