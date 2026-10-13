import os
import json
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from googleapiclient.discovery import build
import gspread
from mcp.server.fastmcp import FastMCP
from datetime import datetime, timezone

mcp = FastMCP("GoogleWorkspaceOAuth")

CLIENT_SECRET_FILE = "/home/idrees/MAK/client_secret_649582304984-fjror9i46o1phb3s3rm4l8tsnr1lut6g.apps.googleusercontent.com.json"
TOKEN_FILE = "/home/idrees/Antigravity/storage/google_token.json"

SCOPES = [
    "https://www.googleapis.com/auth/spreadsheets",
    "https://www.googleapis.com/auth/drive",
    "https://www.googleapis.com/auth/calendar",
    "https://www.googleapis.com/auth/calendar.events",
    "https://mail.google.com/"
]

def get_oauth_credentials():
    creds = None
    if os.path.exists(TOKEN_FILE):
        creds = Credentials.from_authorized_user_file(TOKEN_FILE, SCOPES)
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            if not os.path.exists(CLIENT_SECRET_FILE):
                raise FileNotFoundError(f"OAuth Client Secret not found at {CLIENT_SECRET_FILE}")
            flow = InstalledAppFlow.from_client_secrets_file(CLIENT_SECRET_FILE, SCOPES)
            creds = flow.run_local_server(port=0)
        with open(TOKEN_FILE, "w") as token:
            token.write(creds.to_json())
    return creds

@mcp.tool()
def list_calendar_events(max_results: int = 10) -> str:
    """List upcoming calendar events from your personal Google Calendar via OAuth."""
    try:
        creds = get_oauth_credentials()
        service = build("calendar", "v3", credentials=creds)
        now = datetime.now(timezone.utc).isoformat()
        events_result = service.events().list(
            calendarId="primary",
            timeMin=now,
            maxResults=max_results,
            singleEvents=True,
            orderBy="startTime"
        ).execute()
        events = events_result.get("items", [])
        if not events:
            return "No upcoming calendar events found."

        output = ["=== Your Google Calendar Events ==="]
        for event in events:
            start = event["start"].get("dateTime", event["start"].get("date"))
            summary = event.get("summary", "No Title")
            description = event.get("description", "")
            output.append(f"• Time: {start}\n  Event: {summary}\n  Details: {description}\n")
        return "\n".join(output)
    except Exception as e:
        return f"Google Calendar OAuth error: {e}"

@mcp.tool()
def create_calendar_event(summary: str, start_time_iso: str, end_time_iso: str, description: str = "") -> str:
    """Create a new calendar event on your personal calendar (e.g. 2026-09-26T10:00:00Z)."""
    try:
        creds = get_oauth_credentials()
        service = build("calendar", "v3", credentials=creds)
        event = {
            "summary": summary,
            "description": description,
            "start": {"dateTime": start_time_iso},
            "end": {"dateTime": end_time_iso},
        }
        created_event = service.events().insert(calendarId="primary", body=event).execute()
        return f"Calendar event successfully created: {created_event.get('htmlLink')}"
    except Exception as e:
        return f"Google Calendar creation error: {e}"

@mcp.tool()
def read_google_sheet(spreadsheet_url_or_id: str, worksheet_name: str = "Sheet1", max_rows: int = 25) -> str:
    """Read rows and data from a Google Sheet using your OAuth credentials."""
    try:
        creds = get_oauth_credentials()
        gc = gspread.authorize(creds)
        if "docs.google.com/spreadsheets" in spreadsheet_url_or_id:
            sh = gc.open_by_url(spreadsheet_url_or_id)
        else:
            sh = gc.open_by_key(spreadsheet_url_or_id)

        try:
            ws = sh.worksheet(worksheet_name)
        except Exception:
            ws = sh.get_worksheet(0)

        records = ws.get_all_records()
        if not records:
            all_values = ws.get_all_values()
            return f"Sheet '{sh.title}': Found {len(all_values)} raw rows.\n" + json.dumps(all_values[:max_rows], indent=2)
        return f"Sheet '{sh.title}': {len(records)} records found.\n" + json.dumps(records[:max_rows], indent=2)
    except Exception as e:
        return f"Google Sheets read error: {e}"

@mcp.tool()
def search_google_drive(query: str = "") -> str:
    """Search your Google Drive files using OAuth."""
    try:
        creds = get_oauth_credentials()
        drive_service = build("drive", "v3", credentials=creds)
        q = f"name contains '{query}' and trashed = false" if query else "trashed = false"
        results = drive_service.files().list(q=q, pageSize=20, fields="files(id, name, mimeType, webViewLink)").execute()
        files = results.get("files", [])
        if not files:
            return f"No Google Drive files found matching '{query}'."
        output = ["=== Google Drive Files ==="]
        for f in files:
            output.append(f"• {f['name']} ({f['mimeType']})\n  ID: {f['id']}\n  Link: {f.get('webViewLink', 'N/A')}")
        return "\n".join(output)
    except Exception as e:
        return f"Google Drive search error: {e}"

if __name__ == "__main__":
    mcp.run()
