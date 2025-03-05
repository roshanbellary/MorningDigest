import os
import base64
from datetime import datetime, timedelta
from typing import List, Dict
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from googleapiclient.discovery import build
from email.mime.text import MIMEText
import pickle

# If modifying these scopes, delete the file token.pickle.
SCOPES = ['https://www.googleapis.com/auth/gmail.readonly']

# Get the base directory path
BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

class GmailService:
    def __init__(self):
        self.creds = None
        self.service = None
        
    def authenticate(self):
        """Authenticate with Gmail API using OAuth 2.0"""
        creds = None
        token_path = os.path.join(BASE_DIR, 'token.pickle')
        credentials_path = os.path.join(BASE_DIR, 'credentials.json')
        
        # The file token.pickle stores the user's access and refresh tokens
        if os.path.exists(token_path):
            with open(token_path, 'rb') as token:
                creds = pickle.load(token)
                
        # If there are no (valid) credentials available, let the user log in
        if not creds or not creds.valid:
            if creds and creds.expired and creds.refresh_token:
                creds.refresh(Request())
            else:
                if not os.path.exists(credentials_path):
                    raise FileNotFoundError(
                        f"credentials.json not found at {credentials_path}. "
                        "Please download it from Google Cloud Console and place it in the backend directory."
                    )
                flow = InstalledAppFlow.from_client_secrets_file(
                    credentials_path, SCOPES)
                # Use specific port and host for local server
                creds = flow.run_local_server(
                    host='127.0.0.1',
                    port=8080,
                    redirect_uri_trailing_slash=False,
                    success_message='The authentication flow has completed. You may close this window.',
                    open_browser=True
                )
            # Save the credentials for the next run
            with open(token_path, 'wb') as token:
                pickle.dump(creds, token)

        self.creds = creds
        self.service = build('gmail', 'v1', credentials=creds)
        
    def get_emails_by_date(self, target_date: datetime) -> List[Dict]:
        if not self.service:
            self.authenticate()
            
        # Format date for Gmail query
        next_date = target_date + timedelta(days=1)
        start_date = target_date.strftime('%Y/%m/%d')
        end_date = next_date.strftime('%Y/%m/%d')
        query = f'after:{start_date} before:{end_date}'
        
        try:
            # Get list of messages for the date
            results = self.service.users().messages().list(
                userId='me',
                q=query
            ).execute()
            
            messages = results.get('messages', [])
            emails = []
            
            for message in messages:
                msg = self.service.users().messages().get(
                    userId='me',
                    id=message['id'],
                    format='full'
                ).execute()
                
                # Extract headers
                headers = msg['payload']['headers']
                subject = next(
                    (header['value'] for header in headers if header['name'].lower() == 'subject'),
                    'No Subject'
                )
                sender = next(
                    (header['value'] for header in headers if header['name'].lower() == 'from'),
                    'Unknown Sender'
                )
                
                # Extract body
                if 'parts' in msg['payload']:
                    parts = msg['payload']['parts']
                    body = ''
                    for part in parts:
                        if part['mimeType'] == 'text/plain':
                            body = base64.urlsafe_b64decode(
                                part['body']['data']
                            ).decode('utf-8')
                            break
                else:
                    body = base64.urlsafe_b64decode(
                        msg['payload']['body']['data']
                    ).decode('utf-8')
                
                emails.append({
                    'subject': subject,
                    'sender': sender,
                    'content': body,
                    'timestamp': msg['internalDate'],
                    'identifier': message['id']
                })
                
            return emails
            
        except Exception as e:
            print(f"Error retrieving emails: {e}")
            return []
