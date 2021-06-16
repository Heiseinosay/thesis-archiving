from thesis_archiving import db
from sqlalchemy.dialects.mysql import INTEGER, BOOLEAN
from datetime import datetime
import pytz

class User(db.Model):
    id = db.Column(INTEGER(unsigned=True), primary_key=True)
    username = db.Column(db.String(20), unique=True, nullable=False)
    full_name = db.Column(db.String(64), nullable=False)
    email = db.Column(db.String(64), unique=True)
    password = db.Column(db.String(60), nullable=False)
    is_adviser = db.Column(BOOLEAN())
    is_admin = db.Column(BOOLEAN())
    is_superuser = db.Column(BOOLEAN())
    date_registered = db.Column(db.DateTime, nullable=False, default=lambda:datetime.now(tz=pytz.timezone('Asia/Manila')))
    
    def __repr__(self):
		return f"{self.username} - {self.email}"