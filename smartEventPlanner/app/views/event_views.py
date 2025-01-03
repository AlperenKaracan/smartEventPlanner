from flask import Blueprint, render_template, redirect, url_for, flash, request
from flask_login import login_required, current_user
from app.extensions import db
from app.models import Event, EventAttendee
from app.forms import EventForm

bp = Blueprint('events', __name__, url_prefix='/events')

@bp.route('/create', methods=['GET', 'POST'])
@login_required
def create_event():
    form = EventForm()
    if form.validate_on_submit():
        event = Event(
            name=form.name.data,
            description=form.description.data,
            date=form.date.data,
            location=form.location.data,
            category=form.category.data,
            organizer=current_user
        )
        db.session.add(event)
        db.session.commit()
        flash('Etkinlik başarıyla oluşturuldu!', 'success')
        return redirect(url_for('events.event_details', event_id=event.id))
    return render_template('create_event.html', form=form)

@bp.route('/<int:event_id>')
def event_details(event_id):
    event = Event.query.get_or_404(event_id)
    return render_template('event_details.html', event=event)

@bp.route('/<int:event_id>/join')
@login_required
def join_event(event_id):
    event = Event.query.get_or_404(event_id)
    if EventAttendee.query.filter_by(user_id=current_user.id, event_id=event.id).first():
        flash('Zaten bu etkinliğe katıldınız.', 'warning')
    else:
        attendee = EventAttendee(user_id=current_user.id, event_id=event.id)
        db.session.add(attendee)
        db.session.commit()
        flash('Etkinliğe katıldınız!', 'success')
    return redirect(url_for('events.event_details', event_id=event.id))
