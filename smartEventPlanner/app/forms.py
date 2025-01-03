from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField, TextAreaField, DateTimeField, FileField, BooleanField, SelectField, SelectMultipleField
from wtforms.validators import DataRequired, Email, EqualTo, ValidationError, Optional
from datetime import datetime
from app.models import User
from flask_login import current_user
from flask_wtf.file import FileAllowed

class EmptyForm(FlaskForm):
    pass

class RegistrationForm(FlaskForm):
    username = StringField('Kullanıcı Adı', validators=[DataRequired()])
    email = StringField('E-posta', validators=[DataRequired(), Email()])
    password = PasswordField('Şifre', validators=[DataRequired()])
    confirm_password = PasswordField('Şifre Onayı', validators=[DataRequired(), EqualTo('password')])
    first_name = StringField('Ad', validators=[DataRequired()])
    last_name = StringField('Soyad', validators=[DataRequired()])
    submit = SubmitField('Kayıt Ol')

    def validate_username(self, username):
        user = User.query.filter_by(username=username.data).first()
        if user:
            raise ValidationError('Bu kullanıcı adı zaten alınmış.')

    def validate_email(self, email):
        user = User.query.filter_by(email=email.data).first()
        if user:
            raise ValidationError('Bu e-posta zaten kayıtlı.')

class LoginForm(FlaskForm):
    email = StringField('E-posta', validators=[DataRequired(), Email()])
    password = PasswordField('Şifre', validators=[DataRequired()])
    remember = BooleanField('Beni Hatırla')
    submit = SubmitField('Giriş Yap')

class UpdateProfileForm(FlaskForm):
    username = StringField('Kullanıcı Adı', validators=[DataRequired()])
    email = StringField('E-posta', validators=[DataRequired(), Email()])
    first_name = StringField('Ad', validators=[DataRequired()])
    last_name = StringField('Soyad', validators=[DataRequired()])
    interests = SelectMultipleField('İlgi Alanları', choices=[
        ('Spor', 'Spor'), ('Müzik', 'Müzik'), ('Sanat', 'Sanat'), ('Teknoloji', 'Teknoloji'),
        ('Eğitim', 'Eğitim'), ('Kariyer', 'Kariyer'), ('Yemek', 'Yemek'), ('Seyahat', 'Seyahat'),
        ('Kitap', 'Kitap'), ('Film', 'Film')
    ], validators=[Optional()], render_kw={"multiple": True})

    profile_image = FileField('Profil Resmi Yükle', validators=[FileAllowed(['jpg', 'png', 'jpeg'])])
    submit = SubmitField('Güncelle')

    def validate_username(self, username):
        if username.data != current_user.username:
            user = User.query.filter_by(username=username.data).first()
            if user:
                raise ValidationError('Bu kullanıcı adı zaten alınmış.')

    def validate_email(self, email):
        if email.data != current_user.email:
            user = User.query.filter_by(email=email.data).first()
            if user:
                raise ValidationError('Bu e-posta zaten kayıtlı.')

class EventForm(FlaskForm):
    name = StringField('Etkinlik Adı', validators=[DataRequired()])
    description = TextAreaField('Açıklama', validators=[DataRequired()])
    date = StringField(
        'Tarih ve Saat',
        validators=[DataRequired()],
        render_kw={"placeholder": "YYYY-AA-GG SS:DD", "type": "text"}
    )
    location = SelectField(
        'Konum',
        choices=[
            ('Adana', 'Adana'), ('Adıyaman', 'Adıyaman'), ('Afyonkarahisar', 'Afyonkarahisar'),
            # Diğer şehirler...
        ],
        validators=[DataRequired()]
    )
    category = SelectField(
        'Kategori',
        choices=[
            ('Spor', 'Spor'), ('Müzik', 'Müzik'), ('Sanat', 'Sanat'), ('Teknoloji', 'Teknoloji'),
            ('Eğitim', 'Eğitim'), ('Kariyer', 'Kariyer'), ('Yemek', 'Yemek'),
            ('Seyahat', 'Seyahat'), ('Kitap', 'Kitap'), ('Film', 'Film'),
        ],
        validators=[DataRequired()]
    )
    submit = SubmitField('Kaydet')

class MessageForm(FlaskForm):
    content = TextAreaField('Mesaj', validators=[DataRequired()])
    submit = SubmitField('Gönder')

class RequestResetForm(FlaskForm):
    email = StringField('E-posta', validators=[DataRequired(), Email()])
    submit = SubmitField('Şifre Sıfırlama Linki Gönder')

    def validate_email(self, email):
        user = User.query.filter_by(email=email.data).first()
        if user is None:
            raise ValidationError('Bu e-posta ile kayıtlı bir kullanıcı bulunamadı.')

class ResetPasswordForm(FlaskForm):
    password = PasswordField('Yeni Şifre', validators=[DataRequired()])
    confirm_password = PasswordField('Şifre Onayı', validators=[DataRequired(), EqualTo('password')])
    submit = SubmitField('Şifreyi Güncelle')
