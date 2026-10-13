#!/usr/bin/env python3
"""
LEAD INTELLIGENCE SYSTEM — Production Workflow
===============================================
Processes inbound emails through an AI classification pipeline,
scores leads, drafts replies, routes to a Google Sheet dashboard,
stores context in a knowledge graph, and sends alerts.

Usage:
    # Process latest 5 emails
    python3 pipeline.py

    # Process latest N emails
    python3 pipeline.py --count 10

    # Dry run (classify but don't write to sheet or send alerts)
    python3 pipeline.py --dry-run

    # Process a single test email
    python3 pipeline.py --test

Architecture:
    Gmail IMAP ──► AI Classifier (Gemini) ──► Router
                        │                       │
                   Memory Graph            ┌────┴────┐
                   (prior context)         │         │
                                     Dashboard   Notifier
                                    (Sheets)   (Telegram/Log)
"""
import sys
import os
import argparse
import json
import imaplib
import email
from email.header import decode_header
from datetime import datetime

# Add parent paths for imports
sys.path.insert(0, os.path.dirname(__file__))

from classifier import classify_email, enrich_lead
from dashboard import append_lead, get_dashboard_url, _get_or_create_sheet
from notifier import (
    send_notification, store_lead_memory, recall_lead_context, log_alert
)

# Gmail IMAP credentials (from gmail_engine_mcp.py)
SENDER_EMAIL = "idreesqurashi6@gmail.com"
APP_PASSWORD = "qdrg poyy wvsi lgcn"
IMAP_SERVER = "imap.gmail.com"

# Processed emails tracker (avoid re-processing)
PROCESSED_FILE = os.path.join(os.path.dirname(__file__), "processed_ids.json")


def _load_processed():
    if os.path.exists(PROCESSED_FILE):
        with open(PROCESSED_FILE, "r") as f:
            return set(json.load(f))
    return set()


def _save_processed(ids: set):
    with open(PROCESSED_FILE, "w") as f:
        json.dump(list(ids)[-500:], f)  # Keep last 500


def _decode_header_value(value):
    """Decode email header value handling different encodings."""
    if value is None:
        return ""
    decoded_parts = decode_header(value)
    parts = []
    for part, encoding in decoded_parts:
        if isinstance(part, bytes):
            parts.append(part.decode(encoding or "utf-8", errors="replace"))
        else:
            parts.append(part)
    return " ".join(parts)


def _get_email_body(msg):
    """Extract plain text body from an email message."""
    body = ""
    if msg.is_multipart():
        for part in msg.walk():
            content_type = part.get_content_type()
            if content_type == "text/plain":
                try:
                    body = part.get_payload(decode=True).decode("utf-8", errors="replace")
                    break
                except Exception:
                    continue
    else:
        try:
            body = msg.get_payload(decode=True).decode("utf-8", errors="replace")
        except Exception:
            body = str(msg.get_payload())
    return body[:2000]  # Limit to 2000 chars for AI processing


def fetch_emails(max_count: int = 5) -> list:
    """Fetch recent emails from Gmail via IMAP."""
    try:
        mail = imaplib.IMAP4_SSL(IMAP_SERVER)
        mail.login(SENDER_EMAIL, APP_PASSWORD)
        mail.select("inbox")
        status, data = mail.search(None, "ALL")
        if status != "OK" or not data[0]:
            mail.logout()
            return []

        msg_ids = data[0].split()[-max_count:]
        emails = []

        for msg_id in reversed(msg_ids):
            res, msg_data = mail.fetch(msg_id, "(RFC822)")
            for response_part in msg_data:
                if isinstance(response_part, tuple):
                    msg = email.message_from_bytes(response_part[1])
                    message_id = msg.get("Message-ID", str(msg_id))
                    sender = _decode_header_value(msg.get("From", "Unknown"))
                    subject = _decode_header_value(msg.get("Subject", "No Subject"))
                    date_str = msg.get("Date", "")
                    body = _get_email_body(msg)

                    emails.append({
                        "message_id": message_id,
                        "sender": sender,
                        "subject": subject,
                        "date": date_str,
                        "body": body
                    })

        mail.logout()
        return emails
    except Exception as e:
        print(f"ERROR fetching emails: {e}")
        return []


def process_email(email_data: dict, dry_run: bool = False) -> dict:
    """
    Process a single email through the full pipeline:
    1. Check memory for prior context
    2. Classify with AI
    3. Enrich company data
    4. Write to dashboard
    5. Store in memory graph
    6. Send notifications
    """
    sender = email_data["sender"]
    subject = email_data["subject"]
    body = email_data["body"]

    print(f"\n{'='*60}")
    print(f"PROCESSING: {subject}")
    print(f"FROM: {sender}")
    print(f"{'='*60}")

    # Step 1: Check memory for prior context
    print("  [1/6] Checking memory graph for prior context...")
    # Extract sender name/email for memory lookup
    sender_parts = sender.split("<")
    sender_name_raw = sender_parts[0].strip().strip('"')
    prior_context = recall_lead_context(sender_name_raw)
    if prior_context:
        print(f"  ├─ Found prior context ({len(prior_context)} chars)")
    else:
        print(f"  ├─ No prior interactions found")

    # Step 2: Classify with AI
    print("  [2/6] Classifying with Gemini AI...")
    classification = classify_email(sender, subject, body, prior_context)
    category = classification.get("category", "unknown")
    score = classification.get("score", 0)
    reasoning = classification.get("reasoning", "")
    print(f"  ├─ Category: {category.upper()}")
    print(f"  ├─ Score: {score}/100")
    print(f"  ├─ Reasoning: {reasoning}")

    if dry_run:
        print(f"  [DRY RUN] Skipping dashboard, memory, and notifications")
        return {
            "email": email_data,
            "classification": classification,
            "dry_run": True
        }

    # Step 3: Enrich company data
    print("  [3/6] Enriching company data...")
    info = classification.get("extracted_info", {})
    company = info.get("company", "Unknown")
    enrichment = {}
    if company != "Unknown" and category in ("hot_lead", "warm_lead"):
        enrichment = enrich_lead(company)
        if enrichment.get("enriched"):
            print(f"  ├─ Enriched: {len(enrichment.get('snippets', []))} results found")
        else:
            print(f"  ├─ No enrichment data available")
    else:
        print(f"  ├─ Skipped (not a lead or no company detected)")

    # Step 4: Write to Google Sheet dashboard
    print("  [4/6] Writing to dashboard...")
    sheet_result = append_lead(email_data, classification, enrichment)
    sheet_url = sheet_result.get("sheet_url", "")
    if sheet_result.get("status") == "success":
        print(f"  ├─ Dashboard updated (row {sheet_result.get('row')})")
    else:
        print(f"  ├─ Dashboard error: {sheet_result.get('error', 'unknown')}")

    # Step 5: Store in memory graph
    print("  [5/6] Storing in memory graph...")
    sender_name = info.get("sender_name", "Unknown")
    ask = info.get("ask", "")
    mem_result = store_lead_memory(
        sender_name, company, category,
        f"Subject: {subject}. Ask: {ask}. Score: {score}."
    )
    print(f"  ├─ {mem_result}")

    # Step 6: Send notifications
    print("  [6/6] Routing notifications...")
    notif_result = send_notification(
        category, score, sender, subject, reasoning, sheet_url
    )
    for channel, result in notif_result.items():
        print(f"  ├─ {channel}: {result}")

    print(f"  └─ DONE: {category.upper()} (Score: {score})")

    return {
        "email": email_data,
        "classification": classification,
        "enrichment": enrichment,
        "dashboard": sheet_result,
        "memory": mem_result,
        "notifications": notif_result
    }


def run_pipeline(count: int = 5, dry_run: bool = False):
    """Run the full lead intelligence pipeline."""
    start_time = datetime.now()
    print("\n" + "=" * 60)
    print("  LEAD INTELLIGENCE SYSTEM")
    print(f"  Started: {start_time.strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"  Mode: {'DRY RUN' if dry_run else 'PRODUCTION'}")
    print(f"  Processing: last {count} emails")
    print("=" * 60)

    # Ensure dashboard exists
    if not dry_run:
        print("\nInitializing dashboard...")
        _get_or_create_sheet()
        print(f"Dashboard URL: {get_dashboard_url()}")

    # Fetch emails
    print(f"\nFetching {count} emails from Gmail...")
    emails = fetch_emails(count)
    print(f"Fetched {len(emails)} emails")

    # Load processed IDs
    processed = _load_processed()
    new_emails = [e for e in emails if e["message_id"] not in processed]
    print(f"New (unprocessed): {len(new_emails)}")

    if not new_emails:
        print("\nNo new emails to process. All caught up!")
        return []

    # Process each email
    results = []
    for email_data in new_emails:
        result = process_email(email_data, dry_run)
        results.append(result)
        if not dry_run:
            processed.add(email_data["message_id"])

    # Save processed IDs
    if not dry_run:
        _save_processed(processed)

    # Summary
    elapsed = (datetime.now() - start_time).total_seconds()
    print("\n" + "=" * 60)
    print("  PIPELINE SUMMARY")
    print("=" * 60)
    print(f"  Emails processed: {len(results)}")

    categories = {}
    for r in results:
        cat = r.get("classification", {}).get("category", "unknown")
        categories[cat] = categories.get(cat, 0) + 1
    for cat, count in sorted(categories.items(), key=lambda x: -x[1]):
        print(f"  ├─ {cat}: {count}")

    hot_leads = [r for r in results if r.get("classification", {}).get("category") == "hot_lead"]
    if hot_leads:
        print(f"\n  🔥 HOT LEADS DETECTED: {len(hot_leads)}")
        for hl in hot_leads:
            print(f"     • {hl['email']['sender']} (Score: {hl['classification']['score']})")

    if not dry_run:
        print(f"\n  Dashboard: {get_dashboard_url()}")

    print(f"  Elapsed: {elapsed:.1f}s")
    print("=" * 60)

    return results


def run_test():
    """Process a single synthetic test email to verify the pipeline."""
    print("\n🧪 RUNNING TEST MODE")
    print("Processing a synthetic test email...\n")

    test_email = {
        "message_id": f"test-{datetime.now().timestamp()}",
        "sender": "Sarah Chen <sarah@techventures.io>",
        "subject": "AI Automation for Our Sales Pipeline — Budget Approved",
        "date": datetime.now().strftime("%a, %d %b %Y %H:%M:%S +0000"),
        "body": """Hi there,

I'm the VP of Operations at TechVentures (Series B, 85 employees). We just got 
budget approval to automate our sales pipeline and lead qualification process.

We're looking for someone who can build an intelligent system that:
1. Auto-qualifies inbound leads from our website forms
2. Routes hot leads to the right sales rep based on territory  
3. Drafts personalized follow-up emails
4. Tracks everything in our HubSpot CRM

Our budget is $15K-25K for the initial build, with a $2K/month retainer for 
maintenance and optimization.

Timeline: We'd like to kick off within 2 weeks.

Can we schedule a 30-minute call this week to discuss?

Best,
Sarah Chen
VP of Operations, TechVentures
sarah@techventures.io | (415) 555-0123"""
    }

    result = process_email(test_email, dry_run=False)

    print(f"\n{'='*60}")
    print("TEST RESULT:")
    print(json.dumps({
        "category": result["classification"]["category"],
        "score": result["classification"]["score"],
        "reasoning": result["classification"]["reasoning"],
        "draft_reply_preview": result["classification"]["draft_reply"][:200] + "..."
    }, indent=2))
    print(f"{'='*60}")

    return result


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Lead Intelligence System")
    parser.add_argument("--count", type=int, default=5, help="Number of emails to process")
    parser.add_argument("--dry-run", action="store_true", help="Classify only, no writes")
    parser.add_argument("--test", action="store_true", help="Run with synthetic test email")
    parser.add_argument("--dashboard-url", action="store_true", help="Print dashboard URL")

    args = parser.parse_args()

    if args.dashboard_url:
        print(get_dashboard_url())
    elif args.test:
        run_test()
    else:
        run_pipeline(count=args.count, dry_run=args.dry_run)
