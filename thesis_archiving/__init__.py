from flask import Flask
from thesis_archiving.config import Config

def create_app(config_class=Config):
    app = Flask(__name__)
    app.config.from_object(Config)

    from thesis_archiving.main.routes import main
    from thesis_archiving.thesis.routes import thesis
    from thesis_archiving.user.routes import user
    
    app.register_blueprint(main)
    app.register_blueprint(thesis)
    app.register_blueprint(user)
    

    return app