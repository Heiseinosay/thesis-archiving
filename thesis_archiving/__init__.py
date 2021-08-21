from flask import Flask
from flask_wtf.csrf import CSRFProtect
from thesis_archiving.config import Config
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_bcrypt import Bcrypt
from flask_login import LoginManager
from flask_mail import Mail

# extensions
csrf = CSRFProtect()
db = SQLAlchemy()
migrate = Migrate()
bcrypt = Bcrypt()

login_manager = LoginManager()
login_manager.login_view = "user.login"
login_manager.login_message_category = "danger"

mail = Mail()

def create_app(config_class=Config):
    app = Flask(__name__)
    app.config.from_object(Config)

    # init extensions here
    csrf.init_app(app)
    db.init_app(app)
    migrate.init_app(app, db, compare_type=True)
    bcrypt.init_app(app)
    login_manager.init_app(app)
    mail.init_app(app)

    # blueprints
    from thesis_archiving.main.routes import main
    from thesis_archiving.thesis.routes import thesis
    from thesis_archiving.user.routes import user
    from thesis_archiving.log.routes import log
    from thesis_archiving.program.routes import program
    from thesis_archiving.category.routes import category
    from thesis_archiving.group.routes import group
    from thesis_archiving.quantitative_rating.routes import quantitative_rating
    from thesis_archiving.quantitative_criteria.routes import quantitative_criteria
    from thesis_archiving.individual_rating.routes import individual_rating

    app.register_blueprint(main)
    app.register_blueprint(thesis)
    app.register_blueprint(user)
    app.register_blueprint(log)
    app.register_blueprint(program)
    app.register_blueprint(category)
    app.register_blueprint(group)
    app.register_blueprint(quantitative_rating)
    app.register_blueprint(quantitative_criteria)
    app.register_blueprint(individual_rating)
    
    
    # import models for flask migrate
    import thesis_archiving.models

    return app