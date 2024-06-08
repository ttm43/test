from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_session import Session
from flask_mail import Mail
from config import Config

db = SQLAlchemy()
mail = Mail()

def create_app(config_class=Config):
    app = Flask(__name__)
    app.config.from_object(config_class)
    
    db.init_app(app)
    mail.init_app(app)
    
    app.config['SESSION_TYPE'] = 'filesystem'
    Session(app)
    
    from .routes import main as main_blueprint
    app.register_blueprint(main_blueprint)

    return app
