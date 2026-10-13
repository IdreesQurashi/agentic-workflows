#!/usr/bin/env python3
"""Autonomous Clinic Email Harvester and Northstars B2B Pitch Engine.

Crawls clinic websites, extracts direct owner/practice emails, performs DNS MX verification,
and generates bespoke 3-line B2B acquisition pitches via the rotating Gemini Flash Lite pool.
"""

import os
import sys
import re
import csv
import json
import time
import random
import socket
import urllib.parse
import urllib.request
from typing import List, Dict, Any, Optional, Set

import dns.resolver
from bs4 import BeautifulSoup

socket.setdefaulttimeout(8)

try:
    from google import genai
except ImportError:
    genai = None

GEMINI_API_KEYS = [
    "YOUR_GEMINI_API_KEY_PLACEHOLDER",
    "YOUR_GEMINI_API_KEY_PLACEHOLDER",
    "YOUR_GEMINI_API_KEY_PLACEHOLDER",
    "YOUR_GEMINI_API_KEY_PLACEHOLDER",
    "YOUR_GEMINI_API_KEY_PLACEHOLDER",
    "YOUR_GEMINI_API_KEY_PLACEHOLDER",
    "YOUR_GEMINI_API_KEY_PLACEHOLDER",
    "YOUR_GEMINI_API_KEY_PLACEHOLDER",
    "YOUR_GEMINI_API_KEY_PLACEHOLDER",
    "YOUR_GEMINI_API_KEY_PLACEHOLDER",
    "YOUR_GEMINI_API_KEY_PLACEHOLDER",
    "YOUR_GEMINI_API_KEY_PLACEHOLDER",
    "YOUR_GEMINI_API_KEY_PLACEHOLDER",
    "YOUR_GEMINI_API_KEY_PLACEHOLDER"
]

current_key_idx = 0

def get_gemini_client():
    global current_key_idx
    if not genai:
        return None
    key = GEMINI_API_KEYS[current_key_idx % len(GEMINI_API_KEYS)]
    current_key_idx += 1
    return genai.Client(api_key=key)

IGNORED_EMAIL_DOMAINS = {
    "sentry.io", "wixpress.com", "example.com", "domain.com", "yourdomain.com",
    "squarespace.com", "wix.com", "wordpress.org", "gravatar.com", "cloudflare.com",
    "googleapis.com", "schema.org", "bootstrap.com"
}

DISALLOWED_PREFIXES = ("noreply@", "no-reply@", "donotreply@", "support@")

JUNK_EXTENSIONS = ('.png', '.jpg', '.jpeg', '.webp', '.svg', '.gif', '.css', '.js')

def extract_emails_from_html(html: str, target_domain: str) -> Set[str]:
    found = set()
    for match in re.findall(r'mailto:([a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+)', html, re.I):
        found.add(match.strip().lower())
        
    for match in re.findall(r'[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+', html):
        clean = match.strip().lower()
        if not clean.endswith(JUNK_EXTENSIONS):
            parts = clean.split('@')
            if len(parts) == 2 and parts[1] not in IGNORED_EMAIL_DOMAINS:
                if not any(clean.startswith(p) for p in DISALLOWED_PREFIXES):
                    found.add(clean)
                
    domain_emails = [e for e in found if target_domain in e]
    if domain_emails:
        return set(domain_emails)
    return found

def fetch_url_html(url: str) -> Optional[str]:
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36",
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8"
    }
    try:
        req = urllib.request.Request(url, headers=headers)
        with urllib.request.urlopen(req, timeout=6) as resp:
            content_type = resp.headers.get("Content-Type", "")
            if "text/html" not in content_type and "text/plain" not in content_type:
                return None
            return resp.read().decode("utf-8", errors="replace")
    except Exception:
        return None

def verify_mx(email: str) -> bool:
    try:
        domain = email.split('@')[1]
        answers = dns.resolver.resolve(domain, 'MX')
        return len(answers) > 0
    except Exception:
        return False

def harvest_clinic_email(website_url: str) -> Optional[str]:
    if not website_url or not website_url.startswith("http"):
        return None
        
    parsed = urllib.parse.urlparse(website_url)
    base_url = f"{parsed.scheme}://{parsed.netloc}"
    target_domain = parsed.netloc.replace("www.", "").lower()
    
    paths_to_check = [
        website_url,
        f"{base_url}/",
        f"{base_url}/contact",
        f"{base_url}/contact-us",
        f"{base_url}/about",
        f"{base_url}/about-us"
    ]
    
    seen_paths = set()
    for path in paths_to_check:
        if path in seen_paths:
            continue
        seen_paths.add(path)
        html = fetch_url_html(path)
        if not html:
            continue
        emails = extract_emails_from_html(html, target_domain)
        for e in emails:
            if not verify_mx(e):
                continue
            return e
    return None

def generate_northstars_pitch(company: str, city: str, procedure: str) -> Dict[str, str]:
    client = get_gemini_client()
    clean_proc = procedure.split(',')[0].strip() if procedure else "aesthetic"
    
    prompt = f"""Write a strict 3-sentence B2B cold email to the owner of {company}, an established aesthetic clinic in {city}.
Core rules:
1. Never sound like a generic marketing agency selling SEO or ads.
2. Mention you noticed {company}'s strong reputation for {clean_proc} in {city}, but saw gaps in how local patient opportunities are currently captured and converted.
3. Ask if they are opposed to a brief 10-minute strategy call with our founder Muaaz next week to see the breakdown.
4. Do NOT use bracketed placeholders like [Name] or [Owner's Name]. Open directly with: "Hi {company} team,"
5. Output valid JSON only:
{{"subject": "Question regarding {company}", "body": "Hi {company} team,\\n\\n[Sentence 1]. [Sentence 2]. [Sentence 3]\\n\\nBest,\\nIdrees\\nNorthstars Lab"}}"""

    if client:
        try:
            resp = client.models.generate_content(
                model="gemini-flash-lite-latest",
                contents=prompt
            )
            raw = resp.text.strip()
            raw = re.sub(r"^```(?:json)?", "", raw, flags=re.MULTILINE)
            raw = re.sub(r"```$", "", raw, flags=re.MULTILINE).strip()
            data = json.loads(raw)
            if "subject" in data and "body" in data:
                # Scrub any remaining brackets
                clean_body = re.sub(r'\[.*?\]', f'{company} team', data["body"])
                clean_subject = re.sub(r'\[.*?\]', company, data["subject"])
                return {"subject": clean_subject, "body": clean_body}
        except Exception:
            pass

    return {
        "subject": f"Question regarding {company}",
        "body": f"Hi {company} team,\n\nI was looking at established aesthetic practices in {city} offering {clean_proc} and noticed a few clear gaps in how local patient leads are being captured and converted.\n\nWe build acquisition systems specifically for high ticket clinics. Would you be opposed to a brief 10-minute strategy call with our founder Muaaz next week to look at the numbers?\n\nBest,\nIdrees\nNorthstars Lab"
    }

def run_outbound_harvester(max_leads: int = 15):
    input_csv = "/home/idrees/northstars/leads/raw_databases/Combined_400_Fresh_Qualified_Leads.csv"
    output_csv = "/home/idrees/northstars/leads/verified_outreach_ready.csv"
    
    if not os.path.exists(input_csv):
        print(f"Error: {input_csv} not found")
        return
        
    with open(input_csv, mode="r", encoding="utf-8-sig") as f:
        reader = csv.DictReader(f)
        leads = list(reader)
        
    print(f"Loaded {len(leads)} leads. Harvesting direct emails for up to {max_leads} verified targets...")
    
    verified_results = []
    
    for idx, lead in enumerate(leads):
        if len(verified_results) >= max_leads:
            break
            
        company = lead.get("Company Name", "").strip()
        if not company or company.lower() == "clinic":
            continue
            
        website = lead.get("Website", "").strip()
        city = lead.get("City", "Denver").strip()
        procedure = lead.get("Anchor Procedure", "Aesthetics").strip()
        phone = lead.get("Phone", "").strip()
        
        if not website or "location.com" in website or "yelp.com" in website:
            continue
            
        print(f"[{len(verified_results) + 1}/{max_leads}] Crawling: {company} ({website})...")
        email = harvest_clinic_email(website)
        
        if email:
            print(f"   --> Found & MX Verified: {email}")
            pitch = generate_northstars_pitch(company, city, procedure)
            
            verified_results.append({
                "Company Name": company,
                "City": city,
                "Website": website,
                "Phone": phone,
                "Contact Email": email,
                "Anchor Procedure": procedure,
                "Email Subject": pitch["subject"],
                "Email Body": pitch["body"],
                "Status": "READY_FOR_DISPATCH"
            })
            time.sleep(0.3)
        else:
            print("   --> No direct email found on public endpoints.")
            
    fieldnames = [
        "Company Name", "City", "Website", "Phone", "Contact Email",
        "Anchor Procedure", "Email Subject", "Email Body", "Status"
    ]
    
    with open(output_csv, mode="w", encoding="utf-8-sig", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(verified_results)
        
    print(f"\nCompleted! Harvested {len(verified_results)} verified clinic targets with direct pitches.")
    print(f"Saved to: {output_csv}")

if __name__ == "__main__":
    limit = int(sys.argv[1]) if len(sys.argv) > 1 else 10
    run_outbound_harvester(max_leads=limit)
