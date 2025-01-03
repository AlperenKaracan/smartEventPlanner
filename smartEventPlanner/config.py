import os

class Config:

    SECRET_KEY = 'your_secret_key_here'


    SQLALCHEMY_DATABASE_URI = 'postgresql://deneme:2000@localhost:5432/db_name'
    SQLALCHEMY_TRACK_MODIFICATIONS = False


    MAIL_SERVER = 'smtp.gmail.com'
    MAIL_PORT = 587
    MAIL_USE_TLS = True
    MAIL_USERNAME = ''
    MAIL_PASSWORD = ''
    MAIL_DEFAULT_SENDER = ''


    UPLOAD_FOLDER = os.path.join('app', 'static', 'profile_pics')
    ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}


    REMEMBER_COOKIE_DURATION = 3600


    GOOGLE_MAPS_API_KEY = ''
