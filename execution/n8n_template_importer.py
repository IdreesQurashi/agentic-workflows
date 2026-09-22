"""
n8n Template Importer
Fetches workflow templates from the official n8n.io template API
and imports them into a local n8n instance via its REST API.
"""
import os
import sys
import json
import time
import requests
from dotenv import load_dotenv

load_dotenv()

N8N_URL = os.getenv("N8N_URL", "http://localhost:5678").rstrip("/")
N8N_API_KEY = os.getenv("N8N_API_KEY")

HEADERS_LOCAL = {
    "X-N8N-API-KEY": N8N_API_KEY,
    "Accept": "application/json",
    "Content-Type": "application/json",
}

TEMPLATE_API = "https://api.n8n.io/api/templates/workflows"


def fetch_template(template_id: int) -> dict:
    """Fetch the full workflow JSON for a given template ID from n8n.io."""
    url = f"{TEMPLATE_API}/{template_id}"
    resp = requests.get(url, timeout=30)
    resp.raise_for_status()
    return resp.json()


def get_existing_workflow_names() -> set:
    """Return a set of lowercase workflow names already in the local n8n."""
    resp = requests.get(
        f"{N8N_URL}/api/v1/workflows?limit=250", headers=HEADERS_LOCAL, timeout=15
    )
    resp.raise_for_status()
    data = resp.json()
    return {w["name"].strip().lower() for w in data.get("data", [])}


ALLOWED_NODE_KEYS = {
    "id", "name", "type", "typeVersion", "position", "parameters",
    "credentials", "disabled", "notes", "notesInFlow", "webhookId",
    "extendsCredential", "onError", "continueOnFail", "retryOnFail",
    "maxTries", "waitBetweenTries", "alwaysOutputData", "executeOnce",
    "color",
}


def build_import_payload(raw_workflow: dict, name: str, tag: str = "") -> dict:
    """Build a clean payload that the n8n create workflow API accepts."""
    import copy
    wf = copy.deepcopy(raw_workflow)

    tagged_name = f"[{tag}] {name}" if tag else name

    # Clean nodes: strip keys the API rejects (cid, creator, etc.)
    cleaned_nodes = []
    for node in wf.get("nodes", []):
        cleaned_nodes.append({k: v for k, v in node.items() if k in ALLOWED_NODE_KEYS})

    payload = {
        "name": tagged_name,
        "nodes": cleaned_nodes,
        "connections": wf.get("connections", {}),
        "settings": wf.get("settings", {"executionOrder": "v1"}),
    }

    # Only include pinData if present
    if wf.get("pinData"):
        payload["pinData"] = wf["pinData"]

    return payload


def import_workflow(payload: dict) -> dict:
    """Push a workflow payload into local n8n. Returns the API response."""
    resp = requests.post(
        f"{N8N_URL}/api/v1/workflows",
        headers=HEADERS_LOCAL,
        json=payload,
        timeout=30,
    )
    resp.raise_for_status()
    return resp.json()


# ── Curated Template Selection ──────────────────────────────────────────
# Each entry: (template_id, category_tag, short_description)
CURATED_TEMPLATES = [
    # ─── AI Agents & LLM ───
    (6270,  "AI Agent",         "Build Your First AI Agent (99k views)"),
    (5819,  "AI Agent",         "Interactive AI Agent with Chat Interface and Multiple Tools"),
    (8500,  "AI Agent",         "Jarvis: Productivity AI Agent for Tasks, Calendar, Email & Expense using MCPs"),
    (8591,  "AI Agent",         "AI Personal Assistant for Google Tasks"),
    (4723,  "AI Agent",         "AI Personal Assistant (17k views)"),
    (14167, "AI Agent",         "Scrape, search and browse the web with a Firecrawl AI agent"),
    (5398,  "AI Agent",         "AI Assistant with RAG MCP and Search Engine MCP"),
    (5523,  "Multi Agent",      "Evaluate tool usage accuracy in multi-agent AI workflows"),
    (3473,  "Multi Agent",      "Scalable Multi-Agent Chat Using @mentions (12k views)"),
    (3694,  "Multi Agent",      "Multi-Agent AI Clinic Management with WhatsApp, Telegram, Calendar"),
    (6914,  "Multi Agent",      "Creative Design Agency Simulation with OpenAI O3 Multi-Agent"),

    # ─── RAG (Retrieval Augmented Generation) ───
    (5010,  "RAG",              "RAG Starter Template using Vector Stores, Form trigger and OpenAI"),
    (5148,  "RAG",              "Local Chatbot with RAG (28k views)"),
    (4400,  "RAG",              "PDF Document RAG System with Mistral OCR, Qdrant and Gemini AI"),
    (4526,  "RAG",              "Knowledge Base Chatbot with OpenAI, RAG and MongoDB Vectors"),
    (5140,  "RAG",              "Build and Update RAG System with Google Drive, Qdrant, and Gemini"),
    (11807, "RAG",              "Multi-channel support queries with OpenAI RAG and Supabase"),
    (6542,  "RAG",              "All-Source Knowledge Assistant with Claude, RAG, Perplexity, and Drive"),
    (6290,  "RAG",              "Company Website Chatbot Agent (RAG, Calendar integrations)"),
    (5734,  "RAG",              "PDF-Based RAG System with OpenAI, Pinecone and Cohere Reranking"),
    (10157, "RAG",              "Local Document Q&A with Ollama AI, Agentic RAG & PGVector"),

    # ─── Email & Communication ───
    (4722,  "Email",            "Gmail AI Email Manager (29k views)"),
    (5678,  "Email",            "Automate Email Filtering & AI Summarization, free, 24/7"),
    (6287,  "Email",            "Email Support Agent w/ Gemini & GPT fallback using Gmail + Sheets"),
    (3075,  "Email",            "Error handling: Send email via Gmail on execution errors"),
    (5691,  "Sales Email",      "Generate Personalized Sales Emails with LinkedIn Data & Claude"),

    # ─── WhatsApp & Messaging Bots ───
    (4827,  "WhatsApp",         "AI-Powered WhatsApp Chatbot for Text, Voice, Images, PDF with RAG (46k views)"),
    (4966,  "WhatsApp",         "Customer Support WhatsApp Bot with Google Docs KB and Gemini AI"),
    (4484,  "Voice AI",         "Voice AI Chatbot with ElevenLabs and InfraNodus (31k views)"),
    (9429,  "Voice AI",         "Automated Phone Receptionist with Twilio, ElevenLabs & Claude AI"),

    # ─── Content & Social Media ───
    (3066,  "Content",          "Automate Multi-Platform Social Media Content Creation with AI (205k views)"),
    (4352,  "Content",          "AI-Powered Multi-Social Media Post: Google Trends & Perplexity (41k views)"),
    (4968,  "Content",          "Automated LinkedIn Content Creation with GPT-4 and DALL-E"),
    (5817,  "Content",          "Weekly AI Trend Alerter with arXiv and Weaviate"),
    (6067,  "Content",          "Auto-Generate SEO Blog Posts with Perplexity, GPT, Leonardo & WordPress"),
    (5024,  "Content",          "Build Custom Workflows Automatically with GPT-4o, RAG, and Web Search"),

    # ─── Sales & Lead Gen ───
    (7423,  "Lead Gen",         "Lead Generation Agent"),
    (7467,  "Lead Gen",         "LeadBot Autopilot: Chat-to-Lead for Salesforce"),
    (10640, "Lead Gen",         "Scrape Google Maps Business Leads with Apify & GPT-4 Email Extraction"),
    (5948,  "Competitive Intel", "Automated Competitor Pricing Monitor with Bright Data MCP & OpenAI"),

    # ─── Production & Error Handling ───
    (3882,  "Production",       "Error Handling System with PostgreSQL Logging and Rate-Limited Notifications"),
    (9141,  "Production",       "Automated Error Handling with Email Alerts & Smart Workflow Deactivation"),

    # ─── Document Processing ───
    (10566, "Document",         "Process Large Documents with OCR using SubworkflowAI and Gemini"),
    (9048,  "Document",         "AI Resume Screening with GPT-4o & Error Handling | Sheets & Drive"),
    (16030, "Document",         "Screen and score candidate CVs with Google Gemini and Gmail"),

    # ─── Finance & Operations ───
    (10420, "Finance",          "Automated Daily Financial Analysis from Loyverse POS with Sheets & Email"),
    (10531, "Finance",          "AI-Driven Inventory Management with OpenAI Forecasting & ERP"),
    (15694, "Finance",          "Process Gmail invoice PDFs with Gemini OCR, GPT-4o, Slack and Sheets"),
]


def main():
    if not N8N_API_KEY:
        print("ERROR: N8N_API_KEY not found in .env")
        sys.exit(1)

    # Verify connectivity
    try:
        existing_names = get_existing_workflow_names()
        print(f"✓ Connected to n8n at {N8N_URL}")
        print(f"  Existing workflows: {len(existing_names)}")
    except Exception as e:
        print(f"ERROR: Cannot connect to n8n: {e}")
        sys.exit(1)

    imported = 0
    skipped = 0
    failed = 0

    for template_id, tag, description in CURATED_TEMPLATES:
        # Check for duplicates by name (approximate)
        tagged_name_lower = f"[{tag}] ".lower()

        print(f"\n{'='*80}")
        print(f"[{tag}] Template #{template_id}: {description}")

        try:
            # Fetch from n8n.io
            print(f"  ↓ Fetching template from api.n8n.io...")
            template_data = fetch_template(template_id)

            # The API returns the workflow inside a 'workflow' key
            workflow = template_data.get("workflow", {}).get("workflow", {})
            template_name = template_data.get("workflow", {}).get("name", "Unknown")

            if not workflow or not workflow.get("nodes"):
                print(f"  ✗ SKIP: Template returned empty workflow data")
                skipped += 1
                continue

            # Check for duplicate
            check_name = f"[{tag}] {template_name}".strip().lower()
            if check_name in existing_names:
                print(f"  ○ SKIP: Already exists: {template_name}")
                skipped += 1
                continue

            # Import
            print(f"  ↑ Importing: {template_name} ({len(workflow.get('nodes',[]))} nodes)...")
            payload = build_import_payload(workflow, template_name, tag=tag)
            result = import_workflow(payload)
            new_id = result.get("id", "?")
            print(f"  ✓ IMPORTED as workflow ID: {new_id}")
            existing_names.add(check_name)
            imported += 1

            # Small delay to avoid hammering the API
            time.sleep(0.5)

        except requests.exceptions.HTTPError as e:
            status = e.response.status_code if e.response is not None else "?"
            body = ""
            try:
                body = e.response.text[:300]
            except Exception:
                pass
            print(f"  ✗ FAILED (HTTP {status}): {e}")
            if body:
                print(f"    Response: {body}")
            failed += 1
        except Exception as e:
            print(f"  ✗ FAILED: {e}")
            failed += 1

    print(f"\n{'='*80}")
    print(f"DONE: {imported} imported | {skipped} skipped | {failed} failed")
    print(f"Total workflows now: {len(existing_names)}")


if __name__ == "__main__":
    main()
