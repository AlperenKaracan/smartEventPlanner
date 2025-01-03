from flask import Blueprint, render_template, redirect, url_for, flash, request, current_app
from flask_login import login_user, logout_user, login_required, current_user
from itsdangerous import URLSafeTimedSerializer, SignatureExpired, BadSignature
from app.extensions import db
from app.models import User
from app.email_service import send_confirmation_email
from app.forms import RegistrationForm, LoginForm, UpdateProfileForm
from werkzeug.utils import secure_filename
import os

bp = Blueprint('auth', __name__, url_prefix='/auth')

def generate_confirmation_token(email):
    serializer = URLSafeTimedSerializer(current_app.config['SECRET_KEY'])
    return serializer.dumps(email, salt='email-confirmation-salt')

def confirm_token(token, expiration=3600):
    serializer = URLSafeTimedSerializer(current_app.config['SECRET_KEY'])
    try:
        email = serializer.loads(
            token,
            salt='email-confirmation-salt',
            max_age=expiration
        )
    except (SignatureExpired, BadSignature):
        return False
    return email

@bp.route('/register', methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('main.index'))
    form = RegistrationForm()
    if form.validate_on_submit():
        user = User(
            username=form.username.data,
            email=form.email.data,
            first_name=form.first_name.data,
            last_name=form.last_name.data
        )
        user.set_password(form.password.data)
        db.session.add(user)
        db.session.commit()

        token = generate_confirmation_token(user.email)
        send_confirmation_email(user, token)

        flash('Kayıt başarılı! Lütfen e-postanızı doğrulayın.', 'success')
        return redirect(url_for('auth.login'))
    return render_template('register.html', form=form)

@bp.route('/confirm/<token>')
def confirm_email(token):
    email = confirm_token(token)
    if not email:
        flash('Doğrulama bağlantısı geçersiz veya süresi dolmuş.', 'danger')
        return redirect(url_for('main.index'))

    user = User.query.filter_by(email=email).first_or_404()
    if user.is_confirmed:
        flash('Hesabınız zaten doğrulanmış.', 'success')
    else:
        user.is_confirmed = True
        db.session.commit()
        flash('Hesabınız başarıyla doğrulandı.', 'success')
    return redirect(url_for('auth.login'))

@bp.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('main.index'))
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        if user and user.check_password(form.password.data):
            if user.is_confirmed:
                login_user(user, remember=form.remember.data)
                next_page = request.args.get('next')
                return redirect(next_page) if next_page else redirect(url_for('main.index'))
            else:
                flash('Lütfen önce e-postanızı doğrulayın.', 'warning')
                return redirect(url_for('auth.login'))
        else:
            flash('Giriş başarısız. Lütfen bilgilerinizi kontrol edin.', 'danger')
    return render_template('login.html', form=form)

@bp.route('/logout')
@login_required
def logout():
    logout_user()
    flash('Başarıyla çıkış yaptınız.', 'success')
    return redirect(url_for('main.index'))

@bp.route('/profile', methods=['GET', 'POST'])
@login_required
def profile():
    form = UpdateProfileForm()
    if form.validate_on_submit():
        if form.profile_image.data:
            filename = secure_filename(form.profile_image.data.filename)
            image_path = os.path.join(current_app.config['UPLOAD_FOLDER'], filename)
            form.profile_image.data.save(image_path)
            current_user.profile_image = filename
        current_user.username = form.username.data
        current_user.email = form.email.data
        current_user.first_name = form.first_name.data
        current_user.last_name = form.last_name.data
        db.session.commit()
        flash('Profiliniz güncellendi!', 'success')
        return redirect(url_for('auth.profile'))
    elif request.method == 'GET':
        form.username.data = current_user.username
        form.email.data = current_user.email
        form.first_name.data = current_user.first_name
        form.last_name.data = current_user.last_name
    profile_image = url_for('static', filename='profile_pics/' + current_user.profile_image)
    return render_template('profile.html', form=form, profile_image=profile_image)
