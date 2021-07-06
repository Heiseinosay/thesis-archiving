from flask import url_for, current_app
from flask_mail import Message

from thesis_archiving import mail

def send_reset_request(user):
    token = user.get_reset_token()

    msg = Message("Password Reset Request", sender=current_app.config['MAIL_USERNAME'], recipients=[user.email])

    msg.body = f'''
        To reset your password, visit the link: { url_for('user.password_reset', token=token, _external=True) }

        If you did not make this request, please ignore and no changes will be made.

        For further concerns, please contact us through our Facebook page (https://www.facebook.com/CCSSRnD/).
    '''

    mail.send(msg)
