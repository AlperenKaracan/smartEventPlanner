from flask import render_template, redirect, url_for, flash, request
from flask_login import login_required
from app.extensions import db
from app.models import User, Event, Point
from app.utils import admin_required
from app.admin import bp
from app.forms import EmptyForm
from sqlalchemy.sql import func

@bp.route('/users')
@login_required
@admin_required
def user_list():
    users = (
        db.session.query(
            User.id,
            User.username,
            User.email,
            User.first_name,
            User.last_name,
            User.role,
            User.is_confirmed,
            func.coalesce(func.sum(Point.score), 0).label('total_score')
        )
        .outerjoin(Point, User.id == Point.user_id)
        .group_by(User.id)
        .order_by(func.coalesce(func.sum(Point.score), 0).desc())
        .all()
    )
    empty_form = EmptyForm()
    return render_template('admin/user_list.html', users=users, empty_form=empty_form)

@bp.route('/approve_events')
@login_required
@admin_required
def approve_events():
    pending_events = Event.query.filter_by(is_approved=False).all()
    empty_form = EmptyForm()
    return render_template('admin/approve_events.html', events=pending_events, empty_form=empty_form)

@bp.route('/approve_event/<int:event_id>', methods=['POST'])
@login_required
@admin_required
def approve_event(event_id):
    event = Event.query.get_or_404(event_id)
    event.is_approved = True
    db.session.commit()
    flash('Etkinlik onaylandı!', 'success')
    return redirect(url_for('admin.approve_events'))

@bp.route('/update_role/<int:user_id>', methods=['POST'])
@admin_required
def update_role(user_id):
    user = User.query.get_or_404(user_id)
    new_role = request.form.get('role')
    if new_role in ['admin', 'user']:
        user.role = new_role
        db.session.commit()
        flash(f"Kullanıcının rolü başarıyla {new_role} olarak güncellendi.", 'success')
    else:
        flash("Geçersiz rol seçimi.", 'danger')
    return redirect(url_for('admin.user_list'))

@bp.route('/delete_user/<int:user_id>', methods=['POST'])
@login_required
@admin_required
def delete_user(user_id):
    user = User.query.get_or_404(user_id)
    if user.role == 'admin':
        flash("Admin kullanıcıları silemezsiniz.", 'danger')
        return redirect(url_for('admin.user_list'))
    db.session.delete(user)
    db.session.commit()
    flash("Kullanıcı başarıyla silindi.", 'success')
    return redirect(url_for('admin.user_list'))
