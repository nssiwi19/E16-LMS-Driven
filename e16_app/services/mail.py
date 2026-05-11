from flask import render_template, current_app
from flask_mail import Message
from ..extensions import mail

def send_email(to, subject, template_name, **kwargs):
    """
    Sends an HTML email using a template.
    """
    try:
        msg = Message(
            subject=subject,
            recipients=[to] if isinstance(to, str) else to,
            html=render_template(f"emails/{template_name}.html", **kwargs)
        )
        mail.send(msg)
        return True
    except Exception as e:
        current_app.logger.error(f"Failed to send email to {to}: {str(e)}")
        return False
