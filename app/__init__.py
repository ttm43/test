from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_session import Session

db = SQLAlchemy()

def create_app():
    app = Flask(__name__)
    app.config.from_object('config.Config')


    
    print(f"Database URI: {app.config['SQLALCHEMY_DATABASE_URI']}")
    db.init_app(app)
    
    app.config['SESSION_TYPE'] = 'filesystem'
    Session(app)

    from .routes import main
    app.register_blueprint(main)

    return app
