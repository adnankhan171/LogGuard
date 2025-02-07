import smtplib
from envs import app_password
from email.mime.text import MIMEText

subject = 'This is the subject of email'
body = 'This is the body of the email'
# add sender email address
sender = ''
# add recipient email address
recipient = [sender, '']


def send_email(subject, body, sender, recipient):
    msg = MIMEText(body)
    msg['Subject'] = subject
    msg['From'] = sender
    msg['To'] = ', '.join(recipient)

    with smtplib.SMTP_SSL('smtp.gmail.com', 465) as smtp_server:
        smtp_server.login(sender, app_password)
        smtp_server.sendmail(sender, recipient, msg.as_string())
    print('msg sent')


send_email(subject, body, sender, recipient)