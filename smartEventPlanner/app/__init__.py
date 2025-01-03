# app/__init__.py
from flask import Flask
from config import Config
from app.extensions import db, migrate, login_manager, mail, csrf


def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)

    db.init_app(app)
    migrate.init_app(app, db)
    login_manager.init_app(app)
    mail.init_app(app)
    csrf.init_app(app)

    from app.auth import bp as auth_bp
    app.register_blueprint(auth_bp, url_prefix='/auth')

    from app.main import bp as main_bp
    app.register_blueprint(main_bp)

    from app.events import bp as events_bp
    app.register_blueprint(events_bp, url_prefix='/events')

    from app.messaging import bp as messaging_bp
    app.register_blueprint(messaging_bp, url_prefix='/messaging')

    from app.admin import bp as admin_bp
    app.register_blueprint(admin_bp, url_prefix='/admin')

    return app
