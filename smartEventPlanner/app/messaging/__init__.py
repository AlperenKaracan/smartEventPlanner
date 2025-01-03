from flask import Blueprint

bp = Blueprint('messaging', __name__, url_prefix='/messaging')

from app.messaging import routes
