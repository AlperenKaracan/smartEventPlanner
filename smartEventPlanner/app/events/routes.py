from flask import render_template, redirect, url_for, flash, request, abort, jsonify
from flask_login import login_required, current_user
from app.extensions import db
from app.models import Event, EventAttendee, Point
from app.forms import EventForm, EmptyForm
from app.events import bp
from app.utils import admin_required
from datetime import datetime

@bp.route('/create', methods=['GET', 'POST'])
@login_required
def create_event():
    form = EventForm()
    if form.validate_on_submit():
        try:
            date_str = form.date.data
            event_date = datetime.strptime(date_str, "%Y-%m-%d %H:%M")
            event = Event(
                name=form.name.data,
                description=form.description.data,
                date=event_date,
                location=form.location.data,
                category=form.category.data,
                organizer=current_user,
                is_approved=False
            )
            db.session.add(event)
            db.session.commit()
            flash('Etkinlik oluşturuldu! Yönetici onayından sonra yayınlanacaktır.', 'info')
            return redirect(url_for('main.index'))
        except ValueError:
            flash('Tarih formatı hatalı. Lütfen YYYY-AA-GG SS:DD formatında giriniz.', 'danger')
    return render_template('create_event.html', form=form)

@bp.route('/<int:event_id>/edit', methods=['GET', 'POST'])
@login_required
def edit_event(event_id):
    """Etkinlik güncelleme sayfası"""
    event = Event.query.get_or_404(event_id)
    if event.organizer != current_user and not current_user.is_admin():
        abort(403)
    form = EventForm(obj=event)
    if form.validate_on_submit():
        form.populate_obj(event)
        db.session.commit()
        flash('Etkinlik başarıyla güncellendi!', 'success')
        return redirect(url_for('events.event_details', event_id=event.id))
    return render_template('edit_event.html', form=form, event=event)

@bp.route('/<int:event_id>/delete', methods=['POST'])
@login_required
def delete_event(event_id):
    """Etkinlik silme işlemi"""
    event = Event.query.get_or_404(event_id)
    if event.organizer != current_user and not current_user.is_admin():
        abort(403)
    db.session.delete(event)
    db.session.commit()
    flash('Etkinlik başarıyla silindi!', 'success')
    return redirect(url_for('main.index'))

@bp.route('/<int:event_id>')
def event_details(event_id):
    """Etkinlik detayları sayfası"""
    event = Event.query.get_or_404(event_id)
    if not event.is_approved and (not current_user.is_authenticated or not current_user.is_admin()):
        flash("Etkinlik admin onayını bekliyor.", 'warning')
        return redirect(url_for('main.index'))
    form = EventForm(obj=event)
    is_attending = current_user.is_authenticated and EventAttendee.query.filter_by(user_id=current_user.id, event_id=event.id).first()
    return render_template('event_details.html', event=event, form=form, is_attending=is_attending)

@bp.route('/<int:event_id>/join')
@login_required
def join_event(event_id):
    """Etkinliğe katılma işlemi"""
    event = Event.query.get_or_404(event_id)
    if not event.is_approved:
        flash('Bu etkinlik henüz admin tarafından onaylanmamış.', 'warning')
        return redirect(url_for('events.event_list'))
    if not EventAttendee.query.filter_by(user_id=current_user.id, event_id=event.id).first():
        attendee = EventAttendee(user_id=current_user.id, event_id=event.id)
        db.session.add(attendee)
        db.session.commit()
        point = Point(user_id=current_user.id, score=5, badge='Etkinlik Katılımcısı')
        db.session.add(point)
        db.session.commit()
        flash('Etkinliğe katıldınız!', 'success')
    else:
        flash('Zaten bu etkinliğe katıldınız.', 'warning')
    return redirect(url_for('events.event_details', event_id=event.id))

@bp.route('/<int:event_id>/leave')
@login_required
def leave_event(event_id):
    """Etkinlikten ayrılma işlemi"""
    event = Event.query.get_or_404(event_id)
    attendee = EventAttendee.query.filter_by(user_id=current_user.id, event_id=event.id).first()
    if attendee:
        db.session.delete(attendee)
        db.session.commit()
        flash('Etkinlikten ayrıldınız.', 'success')
    else:
        flash('Bu etkinliğe katılmadınız.', 'warning')
    return redirect(url_for('events.event_details', event_id=event.id))

@bp.route('/admin/approve_events')
@login_required
@admin_required
def approve_events():
    """Onay bekleyen etkinliklerin listesi"""
    pending_events = Event.query.filter_by(is_approved=False).all()
    empty_form = EmptyForm()
    return render_template('admin/approve_events.html', events=pending_events, empty_form=empty_form)

@bp.route('/admin/approve_event/<int:event_id>', methods=['POST'])
@login_required
@admin_required
def approve_event(event_id):
    """Etkinliği onaylar"""
    event = Event.query.get_or_404(event_id)
    form = EmptyForm()
    if form.validate_on_submit():
        event.is_approved = True
        db.session.commit()
        flash('Etkinlik onaylandı!', 'success')
    else:
        flash('Onaylama işlemi başarısız oldu. Lütfen tekrar deneyin.', 'danger')
    return redirect(url_for('events.approve_events'))

@bp.route('/calendar', methods=['GET'])
@login_required
def calendar():
    events = Event.query.join(Event.attendees).filter_by(user_id=current_user.id).all()
    return render_template('calendar.html', events=events)

@bp.route('/api/events')
def get_events():
    """Tüm onaylanmış etkinlikleri JSON formatında döndürür"""
    events = Event.query.filter_by(is_approved=True).all()
    events_data = [
        {
            'title': e.name,
            'start': e.date.strftime('%Y-%m-%dT%H:%M:%S'),
            'url': url_for('events.event_details', event_id=e.id, _external=True)
        } for e in events
    ]
    return jsonify(events_data)

@bp.route('/recommendations', methods=['GET'])
def recommendations():
    """Kullanıcı ilgi alanlarına göre etkinlik önerileri"""
    if not current_user.is_authenticated:
        return render_template('recommendations.html', recommended_events=[])
    user_interests = [interest.replace('{', '').replace('}', '').strip().lower()
                      for interest in current_user.interests.split(',')]
    events = Event.query.filter_by(is_approved=True).all()
    recommended_events = [
        event for event in events
        if event.category.lower() in user_interests
    ]
    print("User Interests (Cleaned):", user_interests)
    for event in recommended_events:
        print("Recommended Event:", event.name, "Category:", event.category)
    return render_template('recommendations.html', recommended_events=recommended_events)
