import base64
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from google.oauth2.credentials import Credentials
from google.auth.transport.requests import Request
from google_auth_oauthlib.flow import InstalledAppFlow
import google.auth
from googleapiclient.discovery import build

SCOPES = ['https://www.googleapis.com/auth/gmail.send']

def get_gmail_service():
    creds, _ = google.auth.default()
    service = build('gmail', 'v1', credentials=creds)
    return service


def create_message(sender, to, subject, body):
    message = MIMEMultipart()
    message['to'] = to
    message['from'] = sender
    message['subject'] = subject
    msg = MIMEText(body)
    message.attach(msg)
    raw_message = base64.urlsafe_b64encode(message.as_bytes()).decode('utf-8')
    return {'raw': raw_message}

def send_gmail_api_email(email_address):
    sender_email = email_address  
    email_subject = 'Test Subject'
    email_body = 'This is a test email sent using Gmail API.'
    
    service = get_gmail_service()
    message = create_message(sender_email, email_address, email_subject, email_body)
    
    try:
        sent_message = service.users().messages().send(userId="me", body=message).execute()
        print('Message Id: {}'.format(sent_message['id']))
        print(f"E-posta gönderildi: {email_address}")
    except Exception as error:
        print(f'An error occurred: {error}')


