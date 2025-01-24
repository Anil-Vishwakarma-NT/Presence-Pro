
import sys
import os
# Add the parent directory of 'src' to sys.path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../..")))

import pandas as pd
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
import configparser
from concurrent.futures import ThreadPoolExecutor, as_completed
import time
from retry import retry
from config.notification_config import *


# Load configuration
# config = configparser.ConfigParser()
# config.read('config.ini')

# Configuration variables
attendance_path = AttendanceData
email_file_path = EmployeeEmailData
smtp_server = SMTPServer
smtp_port = SMTPPort
sender_email = SenderEmail
sender_password = SenderPassword
email_subject = EmailSubject
email_body_template_path = EmailBodyTemplate
skip_rows_email_file = SkipRowsEmailFile

# Load email body template
with open(email_body_template_path, 'r') as file:
    email_body_template = file.read()
     
     
def send_email(name, email, dates_of_absence, manager_name, manager_email):
    """Send an email with retries on failure."""
    message = MIMEMultipart()
    message['From'] = sender_email
    message['To'] = email
    message['Subject'] = email_subject
    message.attach(MIMEText(email_body_template.format(
        name=name,
        dates_of_absence=dates_of_absence,
        manager_name=manager_name
    ), 'plain'))

    if manager_email:
        message['Cc'] = manager_email
        recipients = [email, manager_email]
    else:
        recipients = [email]

    with smtplib.SMTP(smtp_server, smtp_port) as server:
        server.starttls()
        server.login(sender_email, sender_password)
        server.sendmail(sender_email, recipients, message.as_string())

    print(f"Email sent to {name} at {email}, CC: {manager_email}")
