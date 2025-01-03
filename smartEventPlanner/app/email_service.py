from flask_mail import Message
from flask import render_template, current_app, url_for
from app.extensions import mail

def send_email(subject, recipients, text_body='', html_body='', sender=None):

    if not sender:
        sender = current_app.config['MAIL_DEFAULT_SENDER']
    msg = Message(subject, sender=sender, recipients=recipients)
    if text_body:
        msg.body = text_body
    if html_body:
        msg.html = html_body
    mail.send(msg)

def send_confirmation_email(user, token):

    subject = "Lütfen E-postanızı Doğrulayın"
    recipients = [user.email]
    confirm_url = url_for('auth.confirm_email', token=token, _external=True)
    html_body = render_template('confirm_email.html', confirm_url=confirm_url, user=user)
    send_email(subject, recipients, html_body=html_body)

def send_reset_email(user):

    token = user.get_reset_token()
    subject = "Şifre Sıfırlama Talebi"
    recipients = [user.email]
    reset_url = url_for('auth.reset_token', token=token, _external=True)
    html_body = render_template('reset_email.html', reset_url=reset_url, user=user)
    send_email(subject, recipients, html_body=html_body)

