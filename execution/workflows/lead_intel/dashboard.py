"""
Google Sheets Dashboard — writes lead data to a tracking sheet.
Uses OAuth credentials from the workspace MCP infrastructure.
"""
import os
import json
from datetime import datetime

TOKEN_FILE = "/home/idrees/Antigravity/storage/google_token.json"
CLIENT_SECRET_FILE = "/home/idrees/MAK/client_secret_649582304984-fjror9i46o1phb3s3rm4l8tsnr1lut6g.apps.googleusercontent.com.json"

SCOPES = [
    "https://www.googleapis.com/auth/spreadsheets",
    "https://www.googleapis.com/auth/drive",
]

# This will be created on first run
DASHBOARD_SHEET_ID = None
DASHBOARD_SHEET_NAME = "Lead Intelligence Dashboard"


def _get_creds():
    from google.oauth2.credentials import Credentials
    from google.auth.transport.requests import Request
    from google_auth_oauthlib.flow import InstalledAppFlow

    creds = None
    if os.path.exists(TOKEN_FILE):
        creds = Credentials.from_authorized_user_file(TOKEN_FILE, SCOPES)
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(CLIENT_SECRET_FILE, SCOPES)
            creds = flow.run_local_server(port=0)
        with open(TOKEN_FILE, "w") as token:
            token.write(creds.to_json())
    return creds


def _get_or_create_sheet():
    """Get the dashboard sheet ID, creating it if it doesn't exist."""
    import gspread

    config_path = os.path.join(os.path.dirname(__file__), "dashboard_config.json")

    # Check if we already have a sheet ID saved
    if os.path.exists(config_path):
        with open(config_path, "r") as f:
            config = json.load(f)
            return config.get("sheet_id")

    # Create a new spreadsheet
    creds = _get_creds()
    gc = gspread.authorize(creds)
    sh = gc.create(DASHBOARD_SHEET_NAME)

    # Set up headers
    ws = sh.sheet1
    ws.update_title("Leads")
    headers = [
        "Timestamp", "From", "Subject", "Category", "Score",
        "Sender Name", "Company", "Budget Signal", "Urgency",
        "Ask", "AI Draft Reply", "Reasoning", "Status",
        "Response Time", "Enrichment"
    ]
    ws.append_row(headers)

    # Format header row bold
    ws.format("A1:O1", {"textFormat": {"bold": True}})

    # Save config
    with open(config_path, "w") as f:
        json.dump({"sheet_id": sh.id, "sheet_url": sh.url}, f, indent=2)

    print(f"Created dashboard: {sh.url}")
    return sh.id


def append_lead(email_data: dict, classification: dict, enrichment: dict = None) -> dict:
    """
    Append a classified lead to the Google Sheet dashboard.

    Args:
        email_data: dict with keys: sender, subject, date
        classification: dict from classifier.classify_email()
        enrichment: optional dict from classifier.enrich_lead()

    Returns:
        dict with status and sheet_url
    """
    import gspread

    try:
        creds = _get_creds()
        gc = gspread.authorize(creds)

        config_path = os.path.join(os.path.dirname(__file__), "dashboard_config.json")
        if os.path.exists(config_path):
            with open(config_path, "r") as f:
                config = json.load(f)
            sh = gc.open_by_key(config["sheet_id"])
            sheet_url = config["sheet_url"]
        else:
            sheet_id = _get_or_create_sheet()
            with open(config_path, "r") as f:
                config = json.load(f)
            sh = gc.open_by_key(config["sheet_id"])
            sheet_url = config["sheet_url"]

        ws = sh.worksheet("Leads")

        info = classification.get("extracted_info", {})
        enrichment_summary = ""
        if enrichment and enrichment.get("enriched"):
            enrichment_summary = " | ".join(enrichment.get("snippets", [])[:2])

        row = [
            datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            email_data.get("sender", ""),
            email_data.get("subject", ""),
            classification.get("category", "unknown"),
            classification.get("score", 0),
            info.get("sender_name", ""),
            info.get("company", ""),
            info.get("budget_signal", ""),
            info.get("urgency", ""),
            info.get("ask", ""),
            classification.get("draft_reply", ""),
            classification.get("reasoning", ""),
            "New",  # Status
            "",  # Response Time (filled when human responds)
            enrichment_summary[:500]  # Truncate enrichment
        ]

        ws.append_row(row, value_input_option="USER_ENTERED")

        # Color code based on category
        row_num = len(ws.get_all_values())
        category = classification.get("category", "")
        color_map = {
            "hot_lead": {"red": 0.85, "green": 1.0, "blue": 0.85},     # green
            "warm_lead": {"red": 1.0, "green": 0.95, "blue": 0.8},     # yellow
            "cold_lead": {"red": 0.95, "green": 0.95, "blue": 0.95},   # grey
            "support": {"red": 0.85, "green": 0.92, "blue": 1.0},      # blue
            "spam": {"red": 1.0, "green": 0.87, "blue": 0.87},         # red
        }
        if category in color_map:
            ws.format(f"A{row_num}:O{row_num}", {
                "backgroundColor": color_map[category]
            })

        return {"status": "success", "sheet_url": sheet_url, "row": row_num}

    except Exception as e:
        return {"status": "error", "error": str(e)}


def get_dashboard_url() -> str:
    """Return the URL of the dashboard sheet."""
    config_path = os.path.join(os.path.dirname(__file__), "dashboard_config.json")
    if os.path.exists(config_path):
        with open(config_path, "r") as f:
            return json.load(f).get("sheet_url", "Not configured")
    return "Dashboard not yet created. Run the pipeline first."
