import json
import urllib.request
from google.oauth2 import service_account
from google.auth.transport.requests import Request

SERVICE_ACCOUNT_FILE = "/home/idrees/Antigravity/storage/google_service_account.json"
SCOPES = [
    "https://www.googleapis.com/auth/spreadsheets",
    "https://www.googleapis.com/auth/drive"
]

def get_auth_token():
    creds = service_account.Credentials.from_service_account_file(
        SERVICE_ACCOUNT_FILE, scopes=SCOPES
    )
    creds.refresh(Request())
    return creds.token

def create_spreadsheet():
    token = get_auth_token()
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json"
    }

    spreadsheet_body = {
        "properties": {
            "title": "PROJECT I2 - Wraps Content Pattern Engine v1"
        },
        "sheets": [
            {
                "properties": {
                    "sheetId": 0,
                    "title": "raw",
                    "gridProperties": {"rowCount": 100, "columnCount": 15}
                }
            },
            {
                "properties": {
                    "sheetId": 1,
                    "title": "patterns",
                    "gridProperties": {"rowCount": 100, "columnCount": 15}
                }
            },
            {
                "properties": {
                    "sheetId": 2,
                    "title": "summary",
                    "gridProperties": {"rowCount": 100, "columnCount": 15}
                }
            }
        ]
    }

    req = urllib.request.Request(
        "https://sheets.googleapis.com/v4/spreadsheets",
        data=json.dumps(spreadsheet_body).encode("utf-8"),
        headers=headers,
        method="POST"
    )

    with urllib.request.urlopen(req) as resp:
        sheet_data = json.loads(resp.read().decode("utf-8"))
    
    sheet_id = sheet_data["spreadsheetId"]
    sheet_url = sheet_data["spreadsheetUrl"]
    print(f"Created Spreadsheet ID: {sheet_id}")
    print(f"URL: {sheet_url}")

    # Set headers in each sheet
    raw_headers = [
        "post_id", "platform", "creator_handle", "source_url", "permanent_media_url",
        "caption_text", "views_count", "likes_count", "comments_count",
        "outlier_multiplier", "ingested_at"
    ]
    patterns_headers = [
        "post_id", "market_segment", "visual_hook_archetype", "visual_composition",
        "audio_profile", "offer_call_to_action", "performance_thesis", "replicability_tier"
    ]
    summary_headers = [
        "rank", "pattern_name", "target_audience", "average_outlier_lift",
        "shot_1_hook", "shot_2_transition", "shot_3_reveal", "audio_direction", "copy_cta_template"
    ]

    update_payload = {
        "valueInputOption": "USER_ENTERED",
        "data": [
            {
                "range": "raw!A1:K1",
                "values": [raw_headers]
            },
            {
                "range": "patterns!A1:H1",
                "values": [patterns_headers]
            },
            {
                "range": "summary!A1:I1",
                "values": [summary_headers]
            }
        ]
    }

    req_update = urllib.request.Request(
        f"https://sheets.googleapis.com/v4/spreadsheets/{sheet_id}/values:batchUpdate",
        data=json.dumps(update_payload).encode("utf-8"),
        headers=headers,
        method="POST"
    )
    with urllib.request.urlopen(req_update) as resp:
        print("Headers added successfully:", resp.status)

    # Share with idreesqurashi6@gmail.com and make link accessible
    perm_payload = {
        "role": "writer",
        "type": "user",
        "emailAddress": "idreesqurashi6@gmail.com"
    }
    req_perm = urllib.request.Request(
        f"https://www.googleapis.com/drive/v3/files/{sheet_id}/permissions",
        data=json.dumps(perm_payload).encode("utf-8"),
        headers=headers,
        method="POST"
    )
    with urllib.request.urlopen(req_perm) as resp:
        print("Shared with idreesqurashi6@gmail.com:", resp.status)

    # Make accessible to anyone with link as viewer/commenter
    link_perm = {
        "role": "writer",
        "type": "anyone"
    }
    req_link = urllib.request.Request(
        f"https://www.googleapis.com/drive/v3/files/{sheet_id}/permissions",
        data=json.dumps(link_perm).encode("utf-8"),
        headers=headers,
        method="POST"
    )
    with urllib.request.urlopen(req_link) as resp:
        print("Link sharing enabled:", resp.status)

    return sheet_id, sheet_url

if __name__ == "__main__":
    create_spreadsheet()
