import sys
from pathlib import Path

EXECUTION_DIR = Path(__file__).resolve().parent.parent
if str(EXECUTION_DIR) not in sys.path:
    sys.path.insert(0, str(EXECUTION_DIR))

from _root import TOKEN_FILE, CREDENTIALS_FILE
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow

SCOPES = ['https://www.googleapis.com/auth/spreadsheets', 'https://www.googleapis.com/auth/drive']

def main():
    creds = None
    if TOKEN_FILE.exists():
        creds = Credentials.from_authorized_user_file(str(TOKEN_FILE), SCOPES)
        print("token.json already exists and is valid.")
        return

    flow = InstalledAppFlow.from_client_secrets_file(str(CREDENTIALS_FILE), SCOPES)
    
    # We print the URL so the user can manually click it if needed.
    auth_url, _ = flow.authorization_url(prompt='consent')
    print("\n" + "=" * 80)
    print("ACTION REQUIRED: We need to generate token.json.")
    print("Click the link below, authorize the app, and it will redirect to localhost.")
    print("=" * 80)
    print(auth_url)
    print("=" * 80 + "\n")
    
    creds = flow.run_local_server(port=8080)
    
    with open(TOKEN_FILE, 'w') as token:
        token.write(creds.to_json())
    
    print("SUCCESS: token.json generated and saved!")

if __name__ == '__main__':
    main()
