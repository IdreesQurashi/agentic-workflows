"""
Gemini AI Classifier — scores and classifies inbound communications.
Uses the 6-key rotating pool targeting gemini-flash-lite-latest.
"""
import json
import os
import random
from google import genai

KEYS_FILE = "/home/idrees/Antigravity/job_agent/gemini_keys_pool.json"
MODEL_ID = "gemini-flash-lite-latest"


def _get_key() -> str:
    """Retrieve next active key from the 6-key rotating pool."""
    if os.path.exists(KEYS_FILE):
        try:
            with open(KEYS_FILE, "r") as f:
                pool = json.load(f)
            keys = pool.get("active_keys", [])
            if keys:
                idx = pool.get("current_index", 0) % len(keys)
                pool["current_index"] = (idx + 1) % len(keys)
                with open(KEYS_FILE, "w") as f:
                    json.dump(pool, f, indent=2)
                return keys[idx]
        except Exception as e:
            print(f"Warning reading key pool: {e}")

    # Fallback to environment variable
    return os.getenv("GEMINI_API_KEY", "YOUR_GEMINI_API_KEY_PLACEHOLDER")


def classify_email(sender: str, subject: str, body_snippet: str, existing_context: str = "") -> dict:
    """
    Classify an inbound email. Returns structured JSON with:
    - category: "hot_lead" | "warm_lead" | "cold_lead" | "support" | "spam" | "personal"
    - score: 0-100 (business value score)
    - reasoning: why this classification
    - draft_reply: suggested reply text
    - extracted_info: dict with name, company, budget_signal, urgency, ask
    """
    prompt = f"""You are an intelligent business email classifier for a digital automation agency.

Analyze this inbound email and return ONLY valid JSON:

SENDER: {sender}
SUBJECT: {subject}
BODY: {body_snippet}

PRIOR CONTEXT ABOUT THIS SENDER (if any):
{existing_context or "No prior interactions recorded."}

Return this exact JSON structure:
{{
  "category": "<hot_lead|warm_lead|cold_lead|support|spam|personal>",
  "score": <0-100>,
  "reasoning": "<1-2 sentence explanation>",
  "draft_reply": "<professional reply draft, 3-5 sentences>",
  "extracted_info": {{
    "sender_name": "<extracted name or 'Unknown'>",
    "company": "<extracted company or 'Unknown'>",
    "budget_signal": "<any budget/pricing mentions or 'None detected'>",
    "urgency": "<low|medium|high>",
    "ask": "<what they want in 1 sentence>"
  }}
}}

SCORING GUIDE:
- 80-100 (hot_lead): Clear buying intent, mentions budget, timeline, or specific project needs
- 50-79 (warm_lead): Interest in services, asking questions, but no clear commitment signals  
- 20-49 (cold_lead): Generic inquiry, informational, no clear fit
- support: Existing client asking for help with delivered work
- spam: Marketing, newsletters, automated notifications, irrelevant
- personal: Personal email not related to business"""

    max_retries = 3
    for attempt in range(max_retries):
        key = _get_key()
        try:
            client = genai.Client(api_key=key)
            response = client.models.generate_content(
                model=MODEL_ID,
                contents=prompt,
                config={"response_mime_type": "application/json"}
            )
            raw_text = response.text.strip()
            # Clean possible markdown wrapping if any
            if raw_text.startswith("```json"):
                raw_text = raw_text[7:]
            if raw_text.startswith("```"):
                raw_text = raw_text[3:]
            if raw_text.endswith("```"):
                raw_text = raw_text[:-3]
            data = json.loads(raw_text.strip())
            return data
        except Exception as e:
            print(f"    [Attempt {attempt+1}/{max_retries}] Classification error: {e}")

    return {
        "category": "error",
        "score": 0,
        "reasoning": "Classification failed across retries",
        "draft_reply": "",
        "extracted_info": {
            "sender_name": "Unknown",
            "company": "Unknown",
            "budget_signal": "None",
            "urgency": "low",
            "ask": "Classification error"
        }
    }


def enrich_lead(company_name: str) -> dict:
    """Quick web enrichment for a company name using DuckDuckGo."""
    try:
        from duckduckgo_search import DDGS
        results = list(DDGS().text(f"{company_name} company overview", max_results=3))
        if results:
            return {
                "enriched": True,
                "snippets": [r.get("body", "") for r in results[:3]],
                "urls": [r.get("href", "") for r in results[:3]]
            }
    except Exception as e:
        print(f"Enrichment error: {e}")
    return {"enriched": False, "snippets": [], "urls": []}
