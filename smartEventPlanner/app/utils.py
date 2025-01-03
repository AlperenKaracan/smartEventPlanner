from app.extensions import db
from app.models import Event, User, Point
from datetime import datetime, timedelta
from functools import wraps
from flask import abort, current_app
from flask_login import current_user
import requests

def populate_events():
    if Event.query.count() == 0:
        user = User.query.first()
        if not user:
            user = User(
                username='user1',
                email='user1@example.com',
                first_name='User',
                last_name='One',
                is_confirmed=True
            )
            user.set_password('password1')
            db.session.add(user)
            db.session.commit()
        events = [
            Event(
                name='Python Workshop',
                description='Temel ve ileri seviye Python konularının işlendiği atölye çalışması.',
                date=datetime.now() + timedelta(days=5),
                location='İstanbul',
                category='Eğitim',
                organizer=user,
                is_approved=True
            ),
            Event(
                name='Flask ile Web Geliştirme',
                description='Flask frameworkü ile web uygulamaları geliştirme eğitimi.',
                date=datetime.now() + timedelta(days=10),
                location='Ankara',
                category='Teknoloji',
                organizer=user,
                is_approved=True
            ),
            Event(
                name='Veri Bilimi Konferansı',
                description='Veri bilimi ve yapay zeka alanındaki yeniliklerin paylaşıldığı konferans.',
                date=datetime.now() + timedelta(days=15),
                location='İzmir',
                category='Konferans',
                organizer=user,
                is_approved=False
            )
        ]
        db.session.bulk_save_objects(events)
        db.session.commit()

def create_admin_user():
    admin = User.query.filter_by(email='admin@example.com').first()
    if not admin:
        admin = User(
            username='admin',
            email='admin@example.com',
            first_name='Admin',
            last_name='User',
            role='admin',
            is_confirmed=True
        )
        admin.set_password('adminpassword')
        db.session.add(admin)
        db.session.commit()

def admin_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not current_user.is_authenticated or not current_user.is_admin():
            abort(403)
        return f(*args, **kwargs)
    return decorated_function

def get_recommended_events(user):
    if not user.interests:
        return []
    interests = [interest.strip().lower() for interest in user.interests.split(',')]
    recommended_events = Event.query.filter(
        Event.category.in_(interests), Event.is_approved == True
    ).all()
    return recommended_events

def get_coordinates(location):
    api_key = current_app.config['GOOGLE_MAPS_API_KEY']
    url = f"https://maps.googleapis.com/maps/api/geocode/json?address={location}&key={api_key}"
    response = requests.get(url)
    if response.status_code == 200:
        data = response.json()
        if data['results']:
            enlem  = data['results'][0]['geometry']['location']['enlem']
            boylam = data['results'][0]['geometry']['location']['boylam']
            return enlem, boylam
    return None, None
