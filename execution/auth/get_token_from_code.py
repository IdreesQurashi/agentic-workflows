import sys
import os
from pathlib import Path
from urllib.parse import urlparse, parse_qs

EXECUTION_DIR = Path(__file__).resolve().parent.parent
if str(EXECUTION_DIR) not in sys.path:
    sys.path.insert(0, str(EXECUTION_DIR))

from _root import TOKEN_FILE, CREDENTIALS_FILE
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow

SCOPES = ['https://www.googleapis.com/auth/spreadsheets', 'https://www.googleapis.com/auth/drive']

def main():
    if len(sys.argv) < 2:
        flow = InstalledAppFlow.from_client_secrets_file(str(CREDENTIALS_FILE), SCOPES)
        flow.redirect_uri = 'http://localhost:8080/'
        auth_url, _ = flow.authorization_url(prompt='consent')
        print(auth_url)
        return

    code_or_url = sys.argv[1]
    code = code_or_url
    if "http" in code_or_url:
        parsed = urlparse(code_or_url)
        qs = parse_qs(parsed.query)
        if 'code' in qs:
            code = qs['code'][0]
        else:
            print("No code found in URL")
            return

    flow = InstalledAppFlow.from_client_secrets_file(str(CREDENTIALS_FILE), SCOPES)
    flow.redirect_uri = 'http://localhost:8080/'
    
    flow.fetch_token(code=code)
    creds = flow.credentials
    
    with open(TOKEN_FILE, 'w') as token:
        token.write(creds.to_json())
    
    print("SUCCESS: token.json generated and saved!")

if __name__ == '__main__':
    main()
