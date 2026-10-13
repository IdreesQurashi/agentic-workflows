"""
Notification Hub — sends alerts through multiple channels.
Directly uses the notifier MCP and memory graph infrastructure.
"""
import json
import sqlite3
import urllib.request
import urllib.parse
import os
from datetime import datetime

# Memory graph database
DB_PATH = "/home/idrees/Antigravity/storage/knowledge_graph.db"

# Alerts log
ALERTS_FILE = "/home/idrees/Antigravity/storage/alerts_log.json"

# Telegram config (set these for live alerts)
TELEGRAM_BOT_TOKEN = os.environ.get("TELEGRAM_BOT_TOKEN", "")
TELEGRAM_CHAT_ID = os.environ.get("TELEGRAM_CHAT_ID", "")


def send_telegram(message: str) -> str:
    """Send a Telegram push notification."""
    if not TELEGRAM_BOT_TOKEN or not TELEGRAM_CHAT_ID:
        return "Telegram not configured (set TELEGRAM_BOT_TOKEN and TELEGRAM_CHAT_ID env vars)"

    try:
        url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage"
        payload = urllib.parse.urlencode({
            "chat_id": TELEGRAM_CHAT_ID,
            "text": message,
            "parse_mode": "Markdown"
        }).encode("utf-8")
        req = urllib.request.Request(url, data=payload, headers={"User-Agent": "LeadIntel/1.0"})
        with urllib.request.urlopen(req, timeout=10) as resp:
            data = json.loads(resp.read().decode("utf-8"))
            if data.get("ok"):
                return "Telegram alert sent"
            return f"Telegram error: {data}"
    except Exception as e:
        return f"Telegram failed: {e}"


def log_alert(title: str, message: str, level: str = "info") -> str:
    """Log an alert to the local alerts ledger."""
    try:
        os.makedirs(os.path.dirname(ALERTS_FILE), exist_ok=True)
        logs = []
        if os.path.exists(ALERTS_FILE):
            with open(ALERTS_FILE, "r") as f:
                logs = json.load(f)

        logs.append({
            "timestamp": datetime.now().isoformat(),
            "title": title,
            "message": message,
            "level": level,
            "source": "lead_intel"
        })
        with open(ALERTS_FILE, "w") as f:
            json.dump(logs[-200:], f, indent=2)  # Keep last 200
        return f"Alert logged: [{level.upper()}] {title}"
    except Exception as e:
        return f"Alert log error: {e}"


def store_lead_memory(sender_name: str, company: str, category: str, details: str) -> str:
    """Store lead interaction in the knowledge graph for future context."""
    try:
        conn = sqlite3.connect(DB_PATH)
        cur = conn.cursor()

        # Ensure tables exist
        cur.execute("""
            CREATE TABLE IF NOT EXISTS entities (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT UNIQUE NOT NULL,
                entity_type TEXT NOT NULL,
                details TEXT,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        cur.execute("""
            CREATE TABLE IF NOT EXISTS relations (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                source_entity TEXT NOT NULL,
                relation TEXT NOT NULL,
                target_entity TEXT NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)

        # Store the lead entity
        entity_name = sender_name if sender_name != "Unknown" else company
        if entity_name == "Unknown":
            conn.close()
            return "Skipped memory storage (no identifiable entity)"

        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M")
        full_details = f"[{timestamp}] Category: {category}. {details}"

        # Check if entity exists and append context
        cur.execute("SELECT details FROM entities WHERE name = ?", (entity_name,))
        existing = cur.fetchone()
        if existing and existing[0]:
            full_details = existing[0] + f"\n{full_details}"

        cur.execute("""
            INSERT INTO entities (name, entity_type, details, updated_at)
            VALUES (?, ?, ?, CURRENT_TIMESTAMP)
            ON CONFLICT(name) DO UPDATE SET
                details = excluded.details,
                updated_at = CURRENT_TIMESTAMP
        """, (entity_name, "lead", full_details))

        # Link company if both name and company are known
        if sender_name != "Unknown" and company != "Unknown":
            cur.execute("""
                INSERT INTO relations (source_entity, relation, target_entity)
                VALUES (?, ?, ?)
            """, (sender_name, "works_at", company))

        conn.commit()
        conn.close()
        return f"Memory stored for '{entity_name}'"
    except Exception as e:
        return f"Memory storage error: {e}"


def recall_lead_context(search_term: str) -> str:
    """Recall prior interactions with a lead from the knowledge graph."""
    try:
        conn = sqlite3.connect(DB_PATH)
        conn.row_factory = sqlite3.Row
        cur = conn.cursor()

        cur.execute("""
            SELECT * FROM entities 
            WHERE name LIKE ? OR details LIKE ?
        """, (f"%{search_term}%", f"%{search_term}%"))
        entities = cur.fetchall()

        cur.execute("""
            SELECT * FROM relations 
            WHERE source_entity LIKE ? OR target_entity LIKE ?
        """, (f"%{search_term}%", f"%{search_term}%"))
        relations = cur.fetchall()

        conn.close()

        if not entities and not relations:
            return ""

        parts = []
        for e in entities:
            parts.append(f"[{e['entity_type']}] {e['name']}: {e['details']}")
        for r in relations:
            parts.append(f"{r['source_entity']} -> {r['relation']} -> {r['target_entity']}")

        return "\n".join(parts)
    except Exception:
        return ""


def send_notification(category: str, score: int, sender: str, subject: str,
                      reasoning: str, sheet_url: str) -> dict:
    """
    Send notifications through appropriate channels based on lead category.

    Hot leads: Telegram + Desktop alert
    Warm leads: Desktop alert only
    Everything else: Just logged
    """
    results = {}

    if category == "hot_lead":
        msg = (
            f"🔥 *HOT LEAD DETECTED* (Score: {score}/100)\n\n"
            f"*From:* {sender}\n"
            f"*Subject:* {subject}\n"
            f"*Why:* {reasoning}\n\n"
            f"[View Dashboard]({sheet_url})"
        )
        results["telegram"] = send_telegram(msg)
        results["alert"] = log_alert(
            f"HOT LEAD: {sender}",
            f"Score {score}. {reasoning}",
            "urgent"
        )

    elif category == "warm_lead":
        results["alert"] = log_alert(
            f"Warm Lead: {sender}",
            f"Score {score}. {reasoning}. Review draft reply in dashboard.",
            "info"
        )

    elif category == "support":
        results["alert"] = log_alert(
            f"Support Request: {sender}",
            f"{subject} — {reasoning}",
            "info"
        )

    else:
        results["alert"] = log_alert(
            f"Email processed: {sender}",
            f"Category: {category}, Score: {score}",
            "debug"
        )

    return results
