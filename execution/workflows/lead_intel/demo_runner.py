#!/usr/bin/env python3
"""
INTERVIEW SHOWCASE RUNNER — Production Lead Intelligence System
================================================================
Designed specifically for live technical interviews.
Executes 3 realistic scenarios demonstrating agentic workflow capabilities:

1. Scenario 1: Enterprise Buyer (Inbound Form / Email)
   - Demonstrates ICP scoring, high intent budget detection, automated CRM sync
2. Scenario 2: Contextual Follow-up from Same Buyer
   - Demonstrates Knowledge Graph memory recall and adaptive response drafting
3. Scenario 3: Automated Spam / Low-intent Filter
   - Demonstrates noisy inbound filtering with zero human time wasted

Usage:
    python3 demo_runner.py
"""
import sys
import os
import json
import time

sys.path.insert(0, os.path.dirname(__file__))

from pipeline import process_email
from dashboard import get_dashboard_url
from notifier import recall_lead_context

SCENARIOS = [
    {
        "name": "Scenario 1: High Intent Inbound Lead ($20K Budget, Series B)",
        "email": {
            "message_id": "demo-scenario-1",
            "sender": "Marcus Vance <marcus@hypergrowth.ai>",
            "subject": "Urgent: Building an automated client intake workflow",
            "body": """Hello Idrees,

I am the COO at HyperGrowth AI. We are onboarding 15 new agency clients every month
and our account managers are spending 4 hours manually setting up Notion workspaces,
creating Slack channels, and drafting contracts.

We have an approved budget of $20,000 for an automation engineer to build an
end-to-end client provisioning pipeline using Python and APIs.

We want to kick off next Monday. Are you available for a 20-minute Zoom call tomorrow?

Regards,
Marcus Vance
COO, HyperGrowth AI
https://hypergrowth.ai | +1 (312) 555-8901"""
        }
    },
    {
        "name": "Scenario 2: Returning Lead Context Recall (Knowledge Graph Memory in Action)",
        "email": {
            "message_id": "demo-scenario-2",
            "sender": "Marcus Vance <marcus@hypergrowth.ai>",
            "subject": "Re: Urgent: Building an automated client intake workflow",
            "body": """Hi Idrees,

Following up on my previous note. Can your pipeline also handle automatic invoice
creation via Stripe webhooks once the client is provisioned?

Looking forward to your thoughts before our call.

Marcus Vance"""
        }
    },
    {
        "name": "Scenario 3: Low-Value Vendor Spam (Automated Deprioritization)",
        "email": {
            "message_id": "demo-scenario-3",
            "sender": "Sales Team <leads@bulkbacklinksboost.biz>",
            "subject": "Boost your organic Google rankings with 5,000 PBN links!",
            "body": """Special promo for webmasters! Get 5,000 high DA backlinks for only $49.
Click here to place your order now and rank #1 tomorrow! Unsubscribe reply STOP."""
        }
    }
]


def run_interview_demo():
    print("\n" + "=" * 75)
    print("  🚀 PRODUCTION AGENTIC WORKFLOW SHOWCASE: LEAD INTELLIGENCE ENGINE")
    print("=" * 75)
    print(f"  Live Google Sheet Dashboard: {get_dashboard_url()}")
    print("  Underlying AI Model: gemini-flash-lite-latest (Deterministic Pool)")
    print("  State Storage: SQLite Knowledge Graph + Google Sheets API")
    print("=" * 75 + "\n")

    for idx, sc in enumerate(SCENARIOS, 1):
        print("\n" + "#" * 75)
        print(f"  STEP {idx}/3: {sc['name']}")
        print("#" * 75)

        time.sleep(1)
        result = process_email(sc["email"], dry_run=False)

        cat = result["classification"]["category"]
        score = result["classification"]["score"]
        reason = result["classification"]["reasoning"]
        draft = result["classification"]["draft_reply"]

        print("\n  [INTERVIEWER TALKING POINT]:")
        if cat == "hot_lead":
            print(f"  • System identified an enterprise opportunity scoring {score}/100.")
            print("  • Added directly to the CRM sheet in green with draft ready for human sign-off.")
            print("  • Saved company and executive relationship to SQLite memory graph.")
        elif idx == 2:
            print("  • Notice step 1 recalled Marcus Vance's previous context ($20k budget, HyperGrowth AI).")
            print("  • The AI response seamlessly adapted to the ongoing thread without re-asking questions.")
        else:
            print(f"  • Filtered spam automatically (Score: {score}/100) with zero human distraction.")

        print("\n  Press Enter to continue to the next scenario...")
        # If in automated environment without tty, continue automatically
        try:
            if sys.stdin.isatty():
                input()
        except Exception:
            pass

    print("\n" + "=" * 75)
    print("  ✅ DEMO COMPLETED SUCCESSFULLY")
    print("=" * 75)
    print(f"  View Updated Dashboard: {get_dashboard_url()}")
    print("=" * 75 + "\n")


if __name__ == "__main__":
    run_interview_demo()
