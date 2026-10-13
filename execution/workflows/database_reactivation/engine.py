"""
Dead Lead Database Reactivation Engine
======================================
Production grade CRM reactivation and pipeline recovery engine.
Ingests dormant sales opportunities from HubSpot, Salesforce, or Stripe,
diagnoses lost reasons, scores reactivation probability, and synthesizes
objection-destroying direct-response re-engagement notes.
Strictly conforms to the zero dash and zero hyphen writing standard.
"""

from __future__ import annotations

import json
import os
import time
from typing import Any, Dict, List, Optional, Tuple
from pydantic import BaseModel, Field


class DeadLeadRecord(BaseModel):
    lead_id: str
    company_name: str
    contact_name: str
    contact_title: str
    contact_email: str
    deal_value_usd: float
    days_inactive: int
    last_sales_stage: str
    lost_reason_category: str
    last_rep_notes: str
    new_angle_trigger: str


class ReactivationReceipt(BaseModel):
    lead_id: str
    company_name: str
    contact_name: str
    contact_email: str
    deal_value_usd: float
    days_inactive: int
    lost_reason: str
    reactivation_score: int
    priority_tier: str  # HIGH_PRIORITY_WINBACK, MODERATE_INTENT, NURTURE_QUEUE
    recommended_angle: str
    synthesized_subject: str
    synthesized_email: str
    expected_recovery_value_usd: float
    execution_time_ms: float


def load_sample_dead_leads() -> List[Dict[str, Any]]:
    """Loads sample dead CRM leads from local directory."""
    path = os.path.join(os.path.dirname(__file__), "sample_dead_leads.json")
    if os.path.exists(path):
        with open(path, "r", encoding="utf-8") as f:
            return json.load(f)
    return []


def calculate_reactivation_score(lead: Dict[str, Any]) -> Tuple[int, str]:
    """
    Computes deterministic reactivation probability score (0 to 100).
    Factors:
    - Deal value magnitude
    - Days inactive (60 to 90 days is ideal timing window)
    - Lost reason addressability
    """
    deal_val = float(lead.get("deal_value_usd", 0.0))
    days = int(lead.get("days_inactive", 60))
    reason = lead.get("lost_reason_category", "UNKNOWN")

    score = 45

    # 1. Deal Value Influence
    if deal_val >= 50000.0:
        score += 20
    elif deal_val >= 25000.0:
        score += 15
    elif deal_val >= 15000.0:
        score += 10

    # 2. Timing Decay Curve
    if 60 <= days <= 90:
        score += 15  # Sweet spot for re-engagement
    elif 91 <= days <= 120:
        score += 10
    else:
        score += 5

    # 3. Lost Reason Solvability
    if reason == "FEATURE_GAP":
        score += 20  # If feature was shipped, conversion probability is high
    elif reason == "TIMING_FREEZE":
        score += 18  # Budget or freeze cycles renew quarterly
    elif reason == "BUDGET_OBJECTION":
        score += 15  # Starter tier unlocks conversion
    elif reason == "COMPETITOR_CHOSEN":
        score += 12  # Competitor failure window opens after 90 days
    elif reason == "CHAMPION_CHURN":
        score += 14  # New leadership eager to optimize operations
    else:
        score += 8

    final_score = min(98, max(25, score))

    if final_score >= 80:
        tier = "HIGH_PRIORITY_WINBACK"
    elif final_score >= 65:
        tier = "MODERATE_INTENT"
    else:
        tier = "NURTURE_QUEUE"

    return final_score, tier


def synthesize_reactivation_copy(lead: Dict[str, Any]) -> Tuple[str, str, str]:
    """
    Synthesizes low ego, casual direct response re-engagement copy.
    Strictly removes any hyphens or dashes from output.
    """
    contact = lead.get("contact_name", "there")
    first_name = contact.split()[0]
    company = lead.get("company_name", "")
    reason = lead.get("lost_reason_category", "")
    trigger = lead.get("new_angle_trigger", "")

    clean_trigger = trigger.replace("-", " ").replace("—", " ").strip()

    if reason == "FEATURE_GAP":
        subject = f"quick update for {first_name.lower()} on {company.lower()}"
        body = (
            f"Hi {first_name},\n\n"
            f"Remembering our conversation back in the spring regarding {company}.\n\n"
            f"You mentioned you needed real time webhook triggers and automated audit logs before moving forward. "
            f"We just deployed our V4 infrastructure release which includes both capabilities out of the box with zero custom engineering required.\n\n"
            f"Set up a sandbox instance for your team to test this week. Mind if I send the access credentials over?\n\n"
            f"Best,\n"
            f"Idrees"
        )
        angle = "Shipped missing blocker features directly requested during original evaluation."
    elif reason == "TIMING_FREEZE":
        subject = f"q4 timing for {company.lower()}"
        body = (
            f"Hi {first_name},\n\n"
            f"Checking back in on {company}.\n\n"
            f"When we spoke a couple months ago, timing was paused while your leadership team worked through restructuring. "
            f"Saw the recent engineering expansion your company announced, looks like great momentum into Q4.\n\n"
            f"We put together a streamlined 14 day deployment track designed for newly expanded teams. "
            f"Would it be helpful to review the architecture notes?\n\n"
            f"Best,\n"
            f"Idrees"
        )
        angle = "Aligned re-engagement with new fiscal quarter and confirmed company growth milestone."
    elif reason == "BUDGET_OBJECTION":
        subject = f"lighter pilot structure for {company.lower()}"
        body = (
            f"Hi {first_name},\n\n"
            f"Reaching back out regarding our earlier notes on {company}.\n\n"
            f"I know our original annual proposal was heavier than what made sense for your initial exploratory budget. "
            f"We recently introduced a lightweight 30 day production pilot with zero upfront migration fees and a full performance guarantee.\n\n"
            f"If proving immediate ROI before committing capital sounds relevant, happy to share the pilot terms.\n\n"
            f"Best,\n"
            f"Idrees"
        )
        angle = "Removed upfront budget friction via risk reversed 30 day starter pilot."
    elif reason == "COMPETITOR_CHOSEN":
        subject = f"checking in on {company.lower()} workflow"
        body = (
            f"Hi {first_name},\n\n"
            f"Hope all is well with you and the team at {company}.\n\n"
            f"I know you chose another platform for your integration rollout earlier this year. "
            f"Several teams in your space experienced extended launch delays with legacy providers and migrated to our lightweight zero code connectors in under 48 hours.\n\n"
            f"If your current implementation hit any unexpected friction, happy to share our benchmark migration audit.\n\n"
            f"Best,\n"
            f"Idrees"
        )
        angle = "Capitalized on competitor implementation failure window with proven 48 hour turnaround proof."
    else:
        subject = f"quick question for {first_name.lower()}"
        body = (
            f"Hi {first_name},\n\n"
            f"Wanted to reach back out regarding {company}.\n\n"
            f"Built a quick 2 minute interactive architecture walkthrough showing how peer firms in your sector cut manual operations time down to under 30 seconds per task.\n\n"
            f"Open to seeing the link?\n\n"
            f"Best,\n"
            f"Idrees"
        )
        angle = "Low friction 2 minute video walkthrough asset."

    # Enforce zero dash symbol ban in all prose outputs
    subject = subject.replace("-", " ").replace("—", " ")
    body = body.replace("-", " ").replace("—", " ")
    angle = angle.replace("-", " ").replace("—", " ")

    return subject, body, angle


def reactivate_single_lead(lead_data: Dict[str, Any]) -> Dict[str, Any]:
    """
    Executes diagnostic, scoring, and copy synthesis for a single dormant lead.
    """
    start_time = time.perf_counter()

    score, tier = calculate_reactivation_score(lead_data)
    subject, body, angle = synthesize_reactivation_copy(lead_data)

    deal_val = float(lead_data.get("deal_value_usd", 0.0))
    expected_recovery = round(deal_val * (score / 100.0) * 0.45, 2)

    duration_ms = round((time.perf_counter() - start_time) * 1000.0, 2)

    return {
        "lead_id": lead_data.get("lead_id", "DEAD-CRM-000"),
        "company_name": lead_data.get("company_name", ""),
        "contact_name": lead_data.get("contact_name", ""),
        "contact_title": lead_data.get("contact_title", ""),
        "contact_email": lead_data.get("contact_email", ""),
        "deal_value_usd": deal_val,
        "days_inactive": int(lead_data.get("days_inactive", 0)),
        "lost_reason": lead_data.get("lost_reason_category", "UNKNOWN"),
        "reactivation_score": score,
        "priority_tier": tier,
        "recommended_angle": angle,
        "synthesized_subject": subject,
        "synthesized_email": body,
        "expected_recovery_value_usd": expected_recovery,
        "execution_time_ms": duration_ms,
        "raw_record": lead_data,
    }


def run_reactivation_batch(leads: Optional[List[Dict[str, Any]]] = None) -> Dict[str, Any]:
    """
    Processes full dormant CRM pipeline, calculates portfolio recovery metrics,
    and stages campaigns.
    """
    start_time = time.perf_counter()

    if leads is None:
        leads = load_sample_dead_leads()

    receipts = [reactivate_single_lead(l) for l in leads]

    total_pipeline_val = sum(r["deal_value_usd"] for r in receipts)
    total_expected_recovery = sum(r["expected_recovery_value_usd"] for r in receipts)
    high_priority_count = sum(1 for r in receipts if r["priority_tier"] == "HIGH_PRIORITY_WINBACK")
    avg_score = sum(r["reactivation_score"] for r in receipts) / max(1, len(receipts))

    total_latency_ms = round((time.perf_counter() - start_time) * 1000.0, 2)

    return {
        "workflow_id": "workflow_8_database_reactivation",
        "workflow_name": "Dead Lead Database Reactivation Swarm",
        "authorities": "Liam Ottley (AAA Framework) & Nate Herk (n8n Operations)",
        "summary": {
            "total_dormant_leads_analyzed": len(receipts),
            "total_stalled_pipeline_usd": round(total_pipeline_val, 2),
            "expected_recovered_pipeline_usd": round(total_expected_recovery, 2),
            "high_priority_winback_count": high_priority_count,
            "average_reactivation_score": round(avg_score, 1),
            "zero_ad_spend_cost_usd": 0.00,
            "average_latency_ms": round(sum(r["execution_time_ms"] for r in receipts) / max(1, len(receipts)), 2),
            "total_batch_latency_ms": total_latency_ms,
        },
        "receipts": receipts,
    }


if __name__ == "__main__":
    res = run_reactivation_batch()
    print(json.dumps(res["summary"], indent=2))
