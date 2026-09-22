"""
_google_auth.py: Shared Google OAuth helper.
Guarantees consistent token and credentials resolution using the ROOT_DIR anchor.
"""
from pathlib import Path
from google.oauth2.credentials import Credentials
from google.auth.transport.requests import Request
from google_auth_oauthlib.flow import InstalledAppFlow
from _root import TOKEN_FILE, CREDENTIALS_FILE

def get_google_creds(scopes: list) -> Credentials:
    """Returns valid Google credentials, refreshing automatically if expired."""
    creds = None
    if TOKEN_FILE.exists():
        creds = Credentials.from_authorized_user_file(str(TOKEN_FILE), scopes)
    
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
            with open(TOKEN_FILE, 'w') as token:
                token.write(creds.to_json())
        elif CREDENTIALS_FILE.exists():
            flow = InstalledAppFlow.from_client_secrets_file(str(CREDENTIALS_FILE), scopes)
            creds = flow.run_local_server(port=8080)
            with open(TOKEN_FILE, 'w') as token:
                token.write(creds.to_json())
    return creds
