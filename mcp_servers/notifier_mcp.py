import json
import os
import urllib.request
import urllib.parse
from datetime import datetime
from mcp.server.fastmcp import FastMCP

mcp = FastMCP("Notifier")

ALERTS_FILE = "/home/idrees/Antigravity/storage/alerts_log.json"

@mcp.tool()
def send_telegram_alert(bot_token: str, chat_id: str, message: str) -> str:
    """Send an instant push alert message to your phone via a Telegram bot."""
    try:
        url = f"https://api.telegram.org/bot{bot_token}/sendMessage"
        payload = urllib.parse.urlencode({"chat_id": chat_id, "text": message}).encode("utf-8")
        req = urllib.request.Request(url, data=payload, headers={"User-Agent": "AntigravityNotifier/1.0"})
        with urllib.request.urlopen(req, timeout=10) as resp:
            data = json.loads(resp.read().decode("utf-8"))
            if data.get("ok"):
                return f"Telegram alert successfully sent to chat {chat_id}."
            return f"Telegram API responded with error: {data}"
    except Exception as e:
        return f"Failed to send Telegram alert: {e}"

@mcp.tool()
def send_webhook_alert(webhook_url: str, title: str, details: str) -> str:
    """Send a notification payload to any custom webhook (Discord, Slack, Make.com, n8n, WhatsApp gateway)."""
    try:
        payload = json.dumps({"title": title, "details": details, "timestamp": str(datetime.now())}).encode("utf-8")
        req = urllib.request.Request(webhook_url, data=payload, headers={"Content-Type": "application/json", "User-Agent": "AntigravityNotifier/1.0"})
        with urllib.request.urlopen(req, timeout=10) as resp:
            return f"Webhook alert successfully dispatched (HTTP status {resp.status})."
    except Exception as e:
        return f"Webhook dispatch error: {e}"

@mcp.tool()
def log_desktop_alert(title: str, message: str, level: str = "urgent") -> str:
    """Log an urgent alert to the local dashboard ledger for instant review."""
    try:
        os.makedirs(os.path.dirname(ALERTS_FILE), exist_ok=True)
        logs = []
        if os.path.exists(ALERTS_FILE):
            with open(ALERTS_FILE, "r", encoding="utf-8") as f:
                logs = json.load(f)
        
        logs.append({
            "timestamp": str(datetime.now()),
            "title": title,
            "message": message,
            "level": level
        })
        with open(ALERTS_FILE, "w", encoding="utf-8") as f:
            json.dump(logs[-100:], f, indent=2)
        return f"Alert recorded in system ledger: [{level.upper()}] {title}"
    except Exception as e:
        return f"Error logging alert: {e}"

if __name__ == "__main__":
    mcp.run()
