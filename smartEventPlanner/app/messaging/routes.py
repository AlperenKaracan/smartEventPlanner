from flask import render_template, redirect, url_for, flash, request
from flask_login import login_required, current_user
from app.extensions import db
from app.models import Message, Event, Point
from app.forms import MessageForm

from app.messaging import bp

@bp.route('/event/<int:event_id>', methods=['GET', 'POST'])
@login_required
def event_messages(event_id):

    event = Event.query.get_or_404(event_id)
    form = MessageForm()
    if form.validate_on_submit():
        message = Message(sender=current_user, event=event, content=form.content.data)
        db.session.add(message)
        db.session.commit()


        point = Point(user_id=current_user.id, score=2, badge='Aktif Üye')
        db.session.add(point)
        db.session.commit()

        flash('Mesaj gönderildi!', 'success')
        return redirect(url_for('messaging.event_messages', event_id=event.id))
    messages = Message.query.filter_by(event_id=event.id).order_by(Message.timestamp.asc()).all()
    return render_template('event_messages.html', event=event, messages=messages, form=form)
