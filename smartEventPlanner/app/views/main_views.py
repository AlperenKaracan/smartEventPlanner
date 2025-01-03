from flask import Blueprint, render_template, request
from app.models import Event

bp = Blueprint('main', __name__)

@bp.route('/')
@bp.route('/index')
def index():
    page = request.args.get('page', 1, type=int)
    events = Event.query.order_by(Event.date.asc()).paginate(page=page, per_page=6)
    return render_template('index.html', events=events)
