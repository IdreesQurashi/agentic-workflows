import sqlite3
import os
from datetime import datetime, date
from mcp.server.fastmcp import FastMCP

mcp = FastMCP("DailyAgenda")

DB_DIR = "/home/idrees/Antigravity/storage"
DB_PATH = os.path.join(DB_DIR, "agenda.db")

def init_db():
    os.makedirs(DB_DIR, exist_ok=True)
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()
    cur.execute("""
        CREATE TABLE IF NOT EXISTS agenda (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT NOT NULL,
            event_time TEXT NOT NULL,
            category TEXT DEFAULT 'general',
            notes TEXT,
            status TEXT DEFAULT 'pending',
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)
    conn.commit()
    conn.close()

init_db()

@mcp.tool()
def add_calendar_event(title: str, event_time: str, category: str = "general", notes: str = "") -> str:
    """Add a new scheduled event, interview, meeting, chore, or reminder to your agenda."""
    try:
        conn = sqlite3.connect(DB_PATH)
        cur = conn.cursor()
        cur.execute(
            "INSERT INTO agenda (title, event_time, category, notes) VALUES (?, ?, ?, ?)",
            (title, event_time, category, notes)
        )
        event_id = cur.lastrowid
        conn.commit()
        conn.close()
        return f"Event #{event_id} successfully scheduled: '{title}' at {event_time} [Category: {category}]"
    except Exception as e:
        return f"Error adding event: {e}"

@mcp.tool()
def view_agenda(filter_date: str = "today") -> str:
    """View events on your agenda. filter_date can be 'today', 'all', or a specific YYYY-MM-DD string."""
    try:
        conn = sqlite3.connect(DB_PATH)
        conn.row_factory = sqlite3.Row
        cur = conn.cursor()
        target = str(date.today()) if filter_date.lower() == "today" else filter_date
        
        if target == "all":
            cur.execute("SELECT * FROM agenda WHERE status = 'pending' ORDER BY event_time ASC")
        else:
            cur.execute("SELECT * FROM agenda WHERE event_time LIKE ? ORDER BY event_time ASC", (f"%{target}%",))
            
        rows = cur.fetchall()
        conn.close()
        if not rows:
            return f"No events scheduled for {target}."
        
        output = [f"=== Agenda for {target} ==="]
        for r in rows:
            output.append(f"[{r['id']}] {r['event_time']} | {r['title']} ({r['category']}) - Status: {r['status']}\n    Notes: {r['notes'] or 'None'}")
        return "\n".join(output)
    except Exception as e:
        return f"Error retrieving agenda: {e}"

@mcp.tool()
def complete_event(event_id: int) -> str:
    """Mark an event or task on your agenda as completed."""
    try:
        conn = sqlite3.connect(DB_PATH)
        cur = conn.cursor()
        cur.execute("UPDATE agenda SET status = 'completed' WHERE id = ?", (event_id,))
        conn.commit()
        conn.close()
        return f"Event #{event_id} marked as completed."
    except Exception as e:
        return f"Error completing event: {e}"

if __name__ == "__main__":
    mcp.run()
