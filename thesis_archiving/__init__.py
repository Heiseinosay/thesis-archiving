from flask import Flask
from flask_wtf.csrf import CSRFProtect
from thesis_archiving.config import Config
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_bcrypt import Bcrypt

# extensions
csrf = CSRFProtect()
db = SQLAlchemy()
migrate = Migrate()
bcrypt = Bcrypt()

def create_app(config_class=Config):
    app = Flask(__name__)
    app.config.from_object(Config)

    # init extensions here
    csrf.init_app(app)
    db.init_app(app)
    migrate.init_app(app, db, compare_type=True)
    bcrypt.init_app(app)

    from thesis_archiving.main.routes import main
    from thesis_archiving.thesis.routes import thesis
    from thesis_archiving.user.routes import user

    # import models for flask migrate
    from thesis_archiving.models import User
    
    app.register_blueprint(main)
    app.register_blueprint(thesis)
    app.register_blueprint(user)
    

    return app