from flask import Flask
from flask_wtf.csrf import CSRFProtect
from thesis_archiving.config import Config

# extensions
csrf = CSRFProtect()

def create_app(config_class=Config):
    app = Flask(__name__)
    app.config.from_object(Config)

    # init extensions here
    csrf.init_app(app)

    from thesis_archiving.main.routes import main
    from thesis_archiving.thesis.routes import thesis
    from thesis_archiving.user.routes import user
    
    app.register_blueprint(main)
    app.register_blueprint(thesis)
    app.register_blueprint(user)
    

    return app