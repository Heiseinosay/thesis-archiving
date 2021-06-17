import secrets

class Config:
    SECRET_KEY = secrets.token_hex(24)

    SQLALCHEMY_DATABASE_URI = 'mysql+mysqlconnector://root:@localhost/thesis_archiving'