import os

class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'you-will-never-guess'
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL') or 'sqlite:///library.db'
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    UPLOAD_FOLDER = 'static/book'
    MAX_CONTENT_LENGTH = 100 * 1024 * 1024  # 100MB

    MAIL_SERVER = 'smtp.gmail.com'
    MAIL_PORT = 465
    MAIL_USE_TLS = False
    MAIL_USE_SSL = True
    MAIL_USERNAME = 'testforitfp'
    MAIL_PASSWORD = 'vwyz xozf zxad svkv'
    MAIL_DEFAULT_SENDER = 'testforitfp@gmail.com'
