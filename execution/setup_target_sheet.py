import json
import urllib.request
from google.oauth2 import service_account
from google.auth.transport.requests import Request

SPREADSHEET_ID = "1xi21FAQT-gr2L5vYcuOxef24bnk0uSTMUC_7Bf5-Oqs"
SERVICE_ACCOUNT_FILE = "/home/idrees/Antigravity/storage/google_service_account.json"

def get_auth_token():
    creds = service_account.Credentials.from_service_account_file(
        SERVICE_ACCOUNT_FILE, scopes=["https://www.googleapis.com/auth/spreadsheets", "https://www.googleapis.com/auth/drive"]
    )
    creds.refresh(Request())
    return creds.token

def setup_sheet():
    token = get_auth_token()
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json"
    }

    # 1. Inspect existing sheets in the spreadsheet
    meta_req = urllib.request.Request(f"https://sheets.googleapis.com/v4/spreadsheets/{SPREADSHEET_ID}", headers=headers)
    with urllib.request.urlopen(meta_req) as resp:
        meta_data = json.loads(resp.read().decode())
    
    existing_sheets = {s["properties"]["title"]: s["properties"]["sheetId"] for s in meta_data.get("sheets", [])}
    print("Existing sheets:", existing_sheets)

    # 2. Add or rename sheets to raw, patterns, summary
    requests = []
    if "Sheet1" in existing_sheets and "raw" not in existing_sheets:
        requests.append({
            "updateSheetProperties": {
                "properties": {
                    "sheetId": existing_sheets["Sheet1"],
                    "title": "raw"
                },
                "fields": "title"
            }
        })
    elif "raw" not in existing_sheets:
        requests.append({"addSheet": {"properties": {"title": "raw"}}})

    if "patterns" not in existing_sheets:
        requests.append({"addSheet": {"properties": {"title": "patterns"}}})

    if "summary" not in existing_sheets:
        requests.append({"addSheet": {"properties": {"title": "summary"}}})

    if requests:
        batch_body = {"requests": requests}
        req_batch = urllib.request.Request(
            f"https://sheets.googleapis.com/v4/spreadsheets/{SPREADSHEET_ID}:batchUpdate",
            data=json.dumps(batch_body).encode("utf-8"),
            headers=headers,
            method="POST"
        )
        with urllib.request.urlopen(req_batch) as resp:
            print("Tabs structure created/updated successfully!")

    # 3. Define headers and rows
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

    # Load 25 real posts
    with open("/home/idrees/Antigravity/Agentic Workflows-20260907T212811Z-1-001/Agentic Workflows/raw_posts.json") as f:
        raw_data = json.load(f)

    with open("/home/idrees/Antigravity/Agentic Workflows-20260907T212811Z-1-001/Agentic Workflows/pattern_analysis.json") as f:
        patterns_data = json.load(f)

    raw_rows = [raw_headers]
    for r in raw_data:
        raw_rows.append([
            r.get("post_id", ""),
            r.get("platform", ""),
            r.get("creator_handle", ""),
            r.get("source_url", ""),
            r.get("permanent_media_url", ""),
            r.get("caption_text", ""),
            r.get("views_count", 0),
            r.get("likes_count", 0),
            r.get("comments_count", 0),
            r.get("outlier_multiplier", 0.0),
            r.get("ingested_at", "")
        ])

    patterns_rows = [patterns_headers]
    for p in patterns_data:
        patterns_rows.append([
            p.get("post_id", ""),
            p.get("market_segment", ""),
            p.get("visual_hook_archetype", ""),
            p.get("visual_composition", ""),
            p.get("audio_profile", ""),
            p.get("offer_call_to_action", ""),
            p.get("performance_thesis", ""),
            p.get("replicability_tier", "")
        ])

    top5 = [
        [
            1,
            "The 3 Second Corner Tuck Macro Hook",
            "Commercial Fleet and Enthusiast",
            "+340% above baseline",
            "Macro extreme close up of heat gun stretching vinyl over compound curved door handle (0 to 3s)",
            "Snap cut to seamless corner tuck without relief cut wrinkle (3 to 6s)",
            "Steadicam pull back revealing full vehicle livery under fluorescent bay lighting (6 to 12s)",
            "Raw shop heat gun hiss into sharp vinyl squeak, followed by heavy bass drop reveal",
            "No wrinkles, no excuses. Commercial fleet wraps engineered to last 7 years. Link in bio for fleet quotes."
        ],
        [
            2,
            "The Satisfying Hood Peel ASMR",
            "B2C Color Change Enthusiasts",
            "+280% above baseline",
            "Single continuous hand pull removing clear protective cap from ultra gloss vinyl (0 to 3s)",
            "Camera pans alongside vinyl peel reflecting studio tube lights (3 to 7s)",
            "Low angle optical glare shot capturing deep metallic flake in sunlight (7 to 15s)",
            "Microphone glued to vinyl edge for pure crisp ASMR peel acoustic, zero music",
            "Satisfying from every angle. Comment your dream car color below. Booking October slots now."
        ],
        [
            3,
            "The Common Installer Mistake Breakdown",
            "Trade Business Owners and Car Enthusiasts",
            "+210% above baseline",
            "Red grease pencil circling a peeling edge on a competitor wrap with bold text: Never Do This (0 to 2s)",
            "Side by side split screen showing failed dry application vs proper wet knifeless tape method (2 to 7s)",
            "Finished panel flush cut with zero exposed factory paint (7 to 14s)",
            "Direct spoken voiceover with confident technical authority and subtle background beat",
            "Why 80% of cheap wraps peel after 6 months. How we guarantee zero adhesive failure. DM for consultation."
        ],
        [
            4,
            "The Commercial Trade Van ROI Flip",
            "B2B Commercial Contractors (Plumbing, HVAC, Electrical)",
            "+195% above baseline",
            "Beat up, faded white work van rolling into the dark garage bay (0 to 3s)",
            "High speed 15x time lapse showing two technicians applying full branded commercial wrap (3 to 8s)",
            "Bright daylight delivery shot with oversized phone number and QR code clearly legible from 50 feet (8 to 15s)",
            "High tempo upbeat electronic track with quick transition swooshes",
            "Turn your work van into a 24/7 rolling billboard. Local contractors get 50+ new calls a month. Request pricing today."
        ],
        [
            5,
            "Sunlight Flake Pop Rolling Shot",
            "Exotic and Luxury Vehicle Owners",
            "+175% above baseline",
            "Wheel rolling in slow motion, sun hits the front fender causing an instant color flip (0 to 3s)",
            "Low gimbal orbit around front bumper showing laser cut emblem insets (3 to 8s)",
            "Full 360 drone orbit at golden hour capturing liquid gloss depth (8 to 15s)",
            "Ambient cinematic deep synth with subtle exhaust note overlay",
            "Paint protection and color change perfection. Protect your investment. DM for luxury package details."
        ]
    ]

    summary_rows = [summary_headers] + top5

    # 4. Write data to each sheet
    update_data = [
        {"range": "raw!A1:K" + str(len(raw_rows)), "values": raw_rows},
        {"range": "patterns!A1:H" + str(len(patterns_rows)), "values": patterns_rows},
        {"range": "summary!A1:I" + str(len(summary_rows)), "values": summary_rows}
    ]

    req_update = urllib.request.Request(
        f"https://sheets.googleapis.com/v4/spreadsheets/{SPREADSHEET_ID}/values:batchUpdate",
        data=json.dumps({"valueInputOption": "USER_ENTERED", "data": update_data}).encode("utf-8"),
        headers=headers,
        method="POST"
    )
    with urllib.request.urlopen(req_update) as resp:
        print("Data and headers successfully written to raw, patterns, and summary tabs!")

if __name__ == "__main__":
    setup_sheet()
