"""
Leads Persistence Database
==========================
Stores all inbound leads with qualification scores, status lifecycle,
and pre-drafted responses for the visual dashboard.
"""
import sqlite3
import os
import json
from datetime import datetime

DB_PATH = "/home/idrees/Antigravity/storage/knowledge_graph.db"


def init_leads_table():
    """Ensure leads table exists in SQLite database."""
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()
    cur.execute("""
        CREATE TABLE IF NOT EXISTS leads (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            timestamp TEXT NOT NULL,
            sender TEXT NOT NULL,
            sender_name TEXT,
            company TEXT,
            subject TEXT NOT NULL,
            body TEXT,
            category TEXT NOT NULL,
            score INTEGER NOT NULL,
            budget_signal TEXT,
            urgency TEXT,
            ask TEXT,
            reasoning TEXT,
            draft_reply TEXT,
            status TEXT DEFAULT 'Pending Review',
            source TEXT DEFAULT 'Inbound'
        )
    """)
    conn.commit()
    conn.close()


init_leads_table()


def save_lead(lead_dict: dict) -> int:
    """Save or update a lead in the database and return row ID."""
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()

    cur.execute("""
        INSERT INTO leads (
            timestamp, sender, sender_name, company, subject, body,
            category, score, budget_signal, urgency, ask, reasoning,
            draft_reply, status, source
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, (
        lead_dict.get("timestamp", datetime.now().strftime("%Y-%m-%d %H:%M:%S")),
        lead_dict.get("sender", "Unknown"),
        lead_dict.get("sender_name", "Unknown"),
        lead_dict.get("company", "Unknown"),
        lead_dict.get("subject", "No Subject"),
        lead_dict.get("body", ""),
        lead_dict.get("category", "cold_lead"),
        lead_dict.get("score", 0),
        lead_dict.get("budget_signal", "None"),
        lead_dict.get("urgency", "low"),
        lead_dict.get("ask", ""),
        lead_dict.get("reasoning", ""),
        lead_dict.get("draft_reply", ""),
        lead_dict.get("status", "Pending Review"),
        lead_dict.get("source", "Inbound")
    ))

    lead_id = cur.lastrowid
    conn.commit()
    conn.close()
    return lead_id


def get_all_leads(limit: int = 50) -> list:
    """Retrieve all leads ordered by timestamp descending."""
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    cur = conn.cursor()
    cur.execute("SELECT * FROM leads ORDER BY id DESC LIMIT ?", (limit,))
    rows = cur.fetchall()
    leads = [dict(r) for r in rows]
    conn.close()
    return leads


def update_lead_status(lead_id: int, new_status: str, updated_draft: str = None) -> bool:
    """Update lead approval status and optionally revised draft text."""
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()
    if updated_draft:
        cur.execute("UPDATE leads SET status = ?, draft_reply = ? WHERE id = ?", (new_status, updated_draft, lead_id))
    else:
        cur.execute("UPDATE leads SET status = ? WHERE id = ?", (new_status, lead_id))
    affected = cur.rowcount
    conn.commit()
    conn.close()
    return affected > 0


def get_pipeline_metrics() -> dict:
    """Compute aggregate pipeline statistics for the dashboard cards."""
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()

    cur.execute("SELECT COUNT(*) FROM leads")
    total_leads = cur.fetchone()[0]

    cur.execute("SELECT COUNT(*) FROM leads WHERE category = 'hot_lead'")
    hot_leads = cur.fetchone()[0]

    cur.execute("SELECT COUNT(*) FROM leads WHERE status = 'Approved & Sent'")
    approved = cur.fetchone()[0]

    cur.execute("SELECT AVG(score) FROM leads WHERE category != 'spam'")
    avg_score = cur.fetchone()[0] or 0.0

    # Rough pipeline value computation ($15,000 baseline per hot lead)
    estimated_pipeline = hot_leads * 20000

    conn.close()
    return {
        "total_leads": total_leads,
        "hot_leads": hot_leads,
        "approved_sent": approved,
        "avg_qualification_score": round(avg_score, 1),
        "estimated_pipeline_value": f"${estimated_pipeline:,.0f}"
    }
