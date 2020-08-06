import os
from sendgrid import SendGridAPIClient
from sendgrid.helpers.mail import Mail

def sendEmail(email):
    message = Mail(
                from_email='Francisco1627@gmail.com',
                to_emails=email,
                subject='Thanks for register at Wallapp',
                html_content='<strong>Welcome to WallApp!</strong>')
    try:
        sg = SendGridAPIClient(os.environ.get('SENDGRID_API_KEY'))
        response = sg.send(message)
        return('Email sended')
    except Exception as e:
        return(e.message)