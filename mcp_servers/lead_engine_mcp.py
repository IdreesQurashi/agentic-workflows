import sqlite3
import json
import dns.resolver
from mcp.server.fastmcp import FastMCP

mcp = FastMCP("LeadEngine")

DB_PATH = "/home/idrees/job_agent/storage/jobs.db"

@mcp.tool()
def query_jobs_db(sql_query: str) -> str:
    """Execute a safe SELECT query against the jobs.db database and return the results as JSON."""
    if not sql_query.strip().upper().startswith("SELECT"):
        return "Error: Only SELECT queries are permitted via this tool."
    try:
        conn = sqlite3.connect(DB_PATH)
        conn.row_factory = sqlite3.Row
        cur = conn.cursor()
        cur.execute(sql_query)
        rows = cur.fetchall()
        result = [dict(row) for row in rows]
        conn.close()
        return json.dumps(result[:50], indent=2, default=str)
    except Exception as e:
        return f"Database Query Error: {e}"

@mcp.tool()
def verify_email_mx(email: str) -> str:
    """Verify MX records for an email address to ensure the domain receives email and will not hard bounce."""
    try:
        if "@" not in email:
            return f"Invalid email format: {email}"
        domain = email.split("@")[1].strip()
        records = dns.resolver.resolve(domain, "MX")
        mx_hosts = [str(r.exchange).rstrip(".") for r in records]
        return f"Domain {domain} is valid with MX records: {', '.join(mx_hosts)}"
    except Exception as e:
        return f"MX Verification failed for {email}: {e}"

@mcp.tool()
def get_pipeline_summary() -> str:
    """Get high level summary count of all jobs, applications, and inbox alerts in jobs.db."""
    try:
        conn = sqlite3.connect(DB_PATH)
        cur = conn.cursor()
        cur.execute("SELECT COUNT(*) FROM jobs")
        total_jobs = cur.fetchone()[0]
        cur.execute("SELECT COUNT(*) FROM applications")
        total_apps = cur.fetchone()[0]
        cur.execute("SELECT COUNT(*) FROM inbox_alerts")
        total_alerts = cur.fetchone()[0]
        conn.close()
        return f"Total Jobs: {total_jobs} | Total Applications Logged: {total_apps} | Inbox Alerts: {total_alerts}"
    except Exception as e:
        return f"Error reading pipeline: {e}"

# Import tools from job_hunter_mcp
import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
from job_hunter_mcp import (
    qualify_jd_strict_11_10 as _qualify_jd_strict_11_10,
    scrape_ashby_board as _scrape_ashby_board,
    scrape_greenhouse_board as _scrape_greenhouse_board,
    scrape_lever_board as _scrape_lever_board,
    scrape_himalayas_remote as _scrape_himalayas_remote,
    fetch_and_clean_jd as _fetch_and_clean_jd,
    verify_email_contact as _verify_email_contact
)

@mcp.tool()
def qualify_jd_strict_11_10(title: str, full_jd_text: str, location_str: str = "") -> str:
    """Deterministic qualification gatekeeper for Holy 30 roles. Enforces role whitelist, location/visa knockouts, and explicit stack tool match."""
    return _qualify_jd_strict_11_10(title, full_jd_text, location_str)

@mcp.tool()
def scrape_ashby_board(company_slug: str, query: str = "") -> str:
    """Query Ashby official posting API for a company (e.g. 'vapi', 'decagon', 'cosine', 'firecrawl'). Returns clean plain text descriptions and direct apply links."""
    return _scrape_ashby_board(company_slug, query)

@mcp.tool()
def scrape_greenhouse_board(board_token: str, query: str = "") -> str:
    """Query Greenhouse official jobs board API for a company (e.g. 'anthropic', 'cohere', 'perplexity')."""
    return _scrape_greenhouse_board(board_token, query)

@mcp.tool()
def scrape_lever_board(company: str, query: str = "") -> str:
    """Query Lever postings API for a company (e.g. 'relevanceai', 'synthesia')."""
    return _scrape_lever_board(company, query)

@mcp.tool()
def scrape_himalayas_remote(query: str = "automation", limit: int = 50) -> str:
    """Query Himalayas official remote jobs API and filter for contractor friendly, worldwide roles."""
    return _scrape_himalayas_remote(query, limit)

@mcp.tool()
def fetch_and_clean_jd(url: str) -> str:
    """Fetch any job description webpage, strip HTML boilerplates and scripts, and return clean plain text of the role."""
    return _fetch_and_clean_jd(url)

@mcp.tool()
def verify_email_contact(email: str) -> str:
    """Execute 3-Step Zero Bounce Verification on an email address (syntax check, DNS MX resolution, SMTP handshake check)."""
    return _verify_email_contact(email)

if __name__ == "__main__":
    mcp.run()
