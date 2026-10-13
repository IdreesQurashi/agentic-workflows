"""
Nick Saraev Inbound Lead Qualification and Booking Swarm
========================================================
Autonomous inbound lead triage and conversion engine.
Parses inbound prospect submissions, executes cognitive BANT
(Budget, Authority, Need, Timeline) scoring, synthesizes objection-free
personalized responses, and routes high-value prospects to Calendly.
"""

from __future__ import annotations

import json
import time
from typing import Any, Dict, List, Optional, Tuple
from pydantic import BaseModel, Field


class InboundInquiry(BaseModel):
    inquiry_id: str
    prospect_name: str
    company_name: str
    work_email: str
    company_size: str
    stated_budget: str
    timeline: str
    inquiry_text: str
    source: str = "web_contact_form"


SAMPLE_INBOUND_LEADS = [
    {
        "inquiry_id": "INB-901",
        "prospect_name": "Daniel Vance",
        "company_name": "Apex Logistics Group",
        "work_email": "daniel@apexlogistics.com",
        "company_size": "50-200 employees",
        "stated_budget": "$5,000 - $10,000/mo",
        "timeline": "Immediate (under 14 days)",
        "inquiry_text": "We are currently losing 30 hours a week on manual invoice entry and freight rate confirmations. We need an autonomous AI workflow that parses bills of lading and syncs into our TMS. Can we deploy this within two weeks?",
        "source": "demo_request_form",
    },
    {
        "inquiry_id": "INB-902",
        "prospect_name": "Melissa Chong",
        "company_name": "Kroma Aesthetics & Laser",
        "work_email": "melissa@kromaspa.com",
        "company_size": "10-50 employees",
        "stated_budget": "$2,500 - $5,000/mo",
        "timeline": "Next 30 days",
        "inquiry_text": "Looking for an AI triage bot for Instagram DM and website leads that qualifies prospective patients and books high ticket consultations directly into Boulevard.",
        "source": "website_chat_widget",
    },
    {
        "inquiry_id": "INB-903",
        "prospect_name": "Tyler Ross",
        "company_name": "Solo Venture",
        "work_email": "tyler@gmail.com",
        "company_size": "1 employee",
        "stated_budget": "Under $500 one-off",
        "timeline": "Someday",
        "inquiry_text": "Do you offer free coaching or cheap prompt templates for beginner scrapers?",
        "source": "contact_page",
    },
    {
        "inquiry_id": "INB-904",
        "prospect_name": "Marcus Webb",
        "company_name": "Meridian Capital Management",
        "work_email": "marcus@meridiancm.com",
        "company_size": "200-500 employees",
        "stated_budget": "$10,000 - $25,000/mo",
        "timeline": "Immediate (ASAP)",
        "inquiry_text": "We manage 14 portfolio companies and our ops team manually pulls KPI data from 6 separate dashboards every Monday. We need an autonomous data aggregation and report generation workflow that runs Sunday night and sends a formatted PDF dossier to our partners by 7am Monday.",
        "source": "direct_referral",
    },
    {
        "inquiry_id": "INB-905",
        "prospect_name": "Dr. Natasha Kim",
        "company_name": "Northside Oral Surgery & Implants",
        "work_email": "natasha@northsideoralsurgery.com",
        "company_size": "10-50 employees",
        "stated_budget": "$2,500 - $5,000/mo",
        "timeline": "Next 30 days",
        "inquiry_text": "Our front desk is overwhelmed handling consult requests, insurance pre-auth follow-ups, and recall reminders simultaneously. We want an AI receptionist workflow that handles all three autonomously and escalates complex cases to our team.",
        "source": "google_ads_form",
    },
    {
        "inquiry_id": "INB-906",
        "prospect_name": "Chris Patel",
        "company_name": "Freelance",
        "work_email": "chris.patel@hotmail.com",
        "company_size": "1 employee",
        "stated_budget": "Under $500 one-off",
        "timeline": "No rush",
        "inquiry_text": "Can you build me a simple chatbot for my personal blog? Budget is around $100.",
        "source": "contact_page",
    },
]


def evaluate_bant(inquiry: Dict[str, Any]) -> Tuple[int, Dict[str, int], str]:
    """
    Computes deterministic BANT score across 4 pillars (0 to 100).
    """
    budget_str = inquiry.get("stated_budget", "").lower()
    text = inquiry.get("inquiry_text", "").lower()
    timeline_str = inquiry.get("timeline", "").lower()
    email = inquiry.get("work_email", "").lower()

    # 1. Budget Score (0 to 25)
    if "10,000" in budget_str or "5,000" in budget_str:
        b_score = 25
    elif "2,500" in budget_str:
        b_score = 20
    elif "1,000" in budget_str:
        b_score = 12
    else:
        b_score = 5

    # 2. Authority Score (0 to 25)
    # Check business email vs free webmail
    if "@gmail.com" in email or "@yahoo.com" in email or "@hotmail.com" in email:
        a_score = 10
    else:
        a_score = 25

    # 3. Need Score (0 to 25)
    if any(k in text for k in ["invoice", "workflow", "autonomous", "triage", "scale", "booking", "tms"]):
        n_score = 25
    elif any(k in text for k in ["prompt", "free", "template", "cheap"]):
        n_score = 5
    else:
        n_score = 15

    # 4. Timeline Score (0 to 25)
    if any(k in timeline_str for k in ["immediate", "14 days", "asap", "two weeks"]):
        t_score = 25
    elif any(k in timeline_str for k in ["30 days", "month"]):
        t_score = 20
    elif "quarter" in timeline_str:
        t_score = 12
    else:
        t_score = 5

    total = b_score + a_score + n_score + t_score
    breakdown = {
        "budget_score": b_score,
        "authority_score": a_score,
        "need_score": n_score,
        "timeline_score": t_score,
    }

    if total >= 80:
        tier = "HIGH_PRIORITY_VIP"
    elif total >= 60:
        tier = "QUALIFIED_GROWTH"
    else:
        tier = "UNQUALIFIED_NURTURE"

    return total, breakdown, tier


def run_inbound_triage(inquiry_data: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
    """
    Executes full inbound triage, BANT qualification, and automated action dispatch.
    """
    start_time = time.perf_counter()

    import random as _random
    if inquiry_data is None:
        inquiry_data = _random.choice(SAMPLE_INBOUND_LEADS)

    name = inquiry_data.get("prospect_name", "there")
    first_name = name.split()[0]
    company = inquiry_data.get("company_name", "your company")
    email = inquiry_data.get("work_email", "")

    total_score, breakdown, tier = evaluate_bant(inquiry_data)

    # Automated action routing
    if tier == "HIGH_PRIORITY_VIP":
        booking_link = "https://calendly.com/idreesqurashi/enterprise-architecture-30min"
        action = "DISPATCHED_VIP_CALENDAR_INVITE"
        auto_response = (
            f"Hi {first_name},\n\n"
            f"Thanks for reaching out about {company}. Reviewed your note regarding your operations and freight rate workflow.\n\n"
            f"We have architected similar autonomous data extraction and TMS ingestion pipelines that cut manual processing time down to under 30 seconds per document with zero human data entry errors.\n\n"
            f"Given your immediate timeline, here is a direct link to grab 20 minutes on my calendar this week so we can review the technical architecture:\n"
            f"{booking_link}\n\n"
            f"Looking forward to speaking,\n"
            f"Idrees"
        )
    elif tier == "QUALIFIED_GROWTH":
        booking_link = "https://calendly.com/idreesqurashi/growth-consultation-20min"
        action = "DISPATCHED_GROWTH_CALENDAR_INVITE"
        auto_response = (
            f"Hi {first_name},\n\n"
            f"Thanks for getting in touch. Read through your requirements for {company}.\n\n"
            f"Our multi agent triage engine connects directly into booking platforms like Boulevard to qualify high value inquiries and confirm appointments automatically.\n\n"
            f"You can choose a convenient time for an introductory consultation here:\n"
            f"{booking_link}\n\n"
            f"Best,\n"
            f"Idrees"
        )
    else:
        booking_link = None
        action = "ROUTED_TO_SELF_SERVE_ACADEMY"
        auto_response = (
            f"Hi {first_name},\n\n"
            f"Thank you for reaching out. At this time our firm focuses strictly on custom enterprise agentic deployments for active businesses.\n\n"
            f"You are welcome to explore our open architecture documentation and case studies on GitHub.\n\n"
            f"Best regards,\n"
            f"Idrees"
        )

    # Clean prose to enforce zero dash rule
    auto_response = auto_response.replace("-", " ").replace("—", " ")

    duration_ms = round((time.perf_counter() - start_time) * 1000.0, 2)

    return {
        "inquiry_id": inquiry_data.get("inquiry_id", "INB-000"),
        "prospect_name": name,
        "company_name": company,
        "work_email": email,
        "bant_score": total_score,
        "qualification_tier": tier,
        "bant_breakdown": breakdown,
        "recommended_action": action,
        "booking_link": booking_link,
        "drafted_response": auto_response,
        "execution_time_ms": duration_ms,
        "raw_inquiry": inquiry_data,
    }


if __name__ == "__main__":
    res = run_inbound_triage()
    print(json.dumps({
        "tier": res["qualification_tier"],
        "score": res["bant_score"],
        "action": res["recommended_action"],
    }, indent=2))
