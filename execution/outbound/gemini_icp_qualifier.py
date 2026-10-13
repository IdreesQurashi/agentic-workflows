#!/usr/bin/env python3
"""Gemini ICP qualification module for B2B aesthetics and med spa leads.

Evaluates clinic websites against strict 3 point ICP rubric using an 8 key rotating pool.
Target Model: gemini-flash-lite-latest
"""

import os
import sys
import json
import time
import random
import re
import argparse
import socket
from typing import Dict, Any, Optional

# Enforce strict global socket timeout on all HTTP/HTTPS API calls
socket.setdefaulttimeout(12)

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

MODEL_CANDIDATES = [
    "gemini-3.6-flash",
    "gemini-3.7-flash",
    "gemini-3.5-flash-lite",
    "gemini-flash-lite-latest"
]

current_key_index = 0

def get_next_client():
    global current_key_index
    if not genai:
        raise RuntimeError("google-genai library not installed. Run in /home/idrees/job_agent/.venv")
    
    key = GEMINI_API_KEYS[current_key_index % len(GEMINI_API_KEYS)]
    current_key_index += 1
    return genai.Client(api_key=key)

def build_prompt(website_text: str) -> str:
    cleaned_snippet = website_text[:3500].strip()
    return f"""Evaluate this medical aesthetics practice against 3 strict ICP rules:
1. Locations: Must operate 2 or fewer physical clinic locations. (If 3 or more locations are mentioned, FAIL. If unspecified, assume 1 and PASS).
2. Business Model: Must actively market services to the public. (If purely referral only or exclusive closed celebrity practice, FAIL).
3. Core Offer: Must offer high margin procedures (Botox, dermal fillers, lasers, RF microneedling, Morpheus8, body sculpting, veneers, plastic surgery). Low ticket only commoditized salons fail.

Website text:
{cleaned_snippet}

Return strict JSON only:
{{"status": "PASS", "reason": "concise explanation"}}
OR
{{"status": "FAIL", "reason": "concise explanation"}}"""

def clean_json_response(raw_text: str) -> Dict[str, Any]:
    cleaned = raw_text.strip()
    cleaned = re.sub(r"^```(?:json)?", "", cleaned, flags=re.MULTILINE)
    cleaned = re.sub(r"```$", "", cleaned, flags=re.MULTILINE)
    cleaned = cleaned.strip()
    
    try:
        return json.loads(cleaned)
    except Exception:
        pass
    
    match = re.search(r"\{.*\}", cleaned, re.DOTALL)
    if match:
        try:
            return json.loads(match.group(0))
        except Exception:
            pass
            
    if "PASS" in raw_text.upper():
        return {"status": "PASS", "reason": "Manual heuristic extracted PASS"}
    return {"status": "FAIL", "reason": "Could not parse JSON qualification response"}

def call_proxy_qualification(prompt: str) -> Optional[Dict[str, Any]]:
    import urllib.request
    proxy_url = "http://localhost:4000/v1/chat/completions"
    payload = {
        "model": "claude-sonnet-5",
        "messages": [
            {"role": "user", "content": prompt}
        ],
        "temperature": 0.1
    }
    
    req = urllib.request.Request(
        proxy_url,
        headers={
            "Content-Type": "application/json",
            "Authorization": "Bearer sk-dummy"
        },
        data=json.dumps(payload).encode("utf-8")
    )
    
    try:
        with urllib.request.urlopen(req, timeout=1.0) as resp:
            data = json.loads(resp.read().decode("utf-8"))
            content = data["choices"][0]["message"]["content"]
            return clean_json_response(content)
    except Exception:
        return None

def heuristic_icp_qualification(website_text: str) -> Dict[str, Any]:
    lower = website_text.lower()
    
    high_margin_keywords = [
        'botox', 'dysport', 'xeomin', 'filler', 'juvederm', 'restylane', 'sculptra', 'radiesse',
        'morpheus8', 'microneedling', 'laser', 'ipl', 'bbl', 'resurfacing', 'body contouring',
        'coolsculpting', 'emsculpt', 'liposuction', 'facelift', 'veneers', 'invisalign', 'blepharoplasty',
        'kybella', 'prp', 'prf', 'hydrafacial', 'chemical peel', 'ultherapy', 'skin tightening'
    ]
    found_procedures = [kw for kw in high_margin_keywords if kw in lower]
    if not found_procedures:
        return {'status': 'FAIL', 'reason': 'No high margin aesthetic or cosmetic procedures identified'}
        
    if 'referral only' in lower or 'by referral only' in lower or 'private members only' in lower:
        return {'status': 'FAIL', 'reason': 'Practice appears to be referral or members only'}
        
    target_cities = ['charlotte', 'nashville', 'denver', 'atlanta', 'portland', 'san diego', 'phoenix', 'seattle', 'tampa', 'las vegas', 'chicago', 'dallas', 'austin', 'miami', 'new york', 'los angeles', 'houston', 'boston']
    cities_count = len(set(c for c in target_cities if re.search(r'\b' + c + r'\b', lower)))
    if cities_count >= 3:
        return {'status': 'FAIL', 'reason': f'Multiple locations detected across {cities_count} metropolitan markets'}
        
    return {
        'status': 'PASS',
        'reason': f'Boutique practice offering high margin procedures: {", ".join(found_procedures[:4])}'
    }

def qualify_practice_text(website_text: str, max_retries: int = 4) -> Dict[str, Any]:
    if not website_text or len(website_text.strip()) < 40:
        return {"status": "FAIL", "reason": "Insufficient text content on website"}
        
    prompt = build_prompt(website_text)

    # Primary Route: High throughput local LiteLLM proxy (if enabled)
    if os.environ.get("USE_LITELLM_PROXY") == "1":
        proxy_result = call_proxy_qualification(prompt)
        if proxy_result and "status" in proxy_result and "FAIL" not in proxy_result.get("reason", ""):
            status = proxy_result["status"].upper()
            proxy_result["status"] = "PASS" if "PASS" in status else "FAIL"
            return proxy_result
    
    # Secondary Fallback: Direct Google GenAI SDK with key rotation and timeout
    import concurrent.futures

    for attempt in range(max_retries):
        model_name = MODEL_CANDIDATES[attempt % len(MODEL_CANDIDATES)]
        executor = concurrent.futures.ThreadPoolExecutor(max_workers=1)
        try:
            client = get_next_client()
            future = executor.submit(
                client.models.generate_content,
                model=model_name,
                contents=prompt
            )
            response = future.result(timeout=8)
            parsed = clean_json_response(response.text)
            status = parsed.get("status", "FAIL").upper()
            if status not in ["PASS", "FAIL"]:
                status = "PASS" if "PASS" in status else "FAIL"
            parsed["status"] = status
            return parsed
        except Exception as e:
            err_msg = str(e).lower()
            if "resource_exhausted" in err_msg or "429" in err_msg or "503" in err_msg or "unavailable" in err_msg:
                time.sleep(random.uniform(0.3, 0.7))
                continue
            time.sleep(0.3)
        finally:
            try:
                executor.shutdown(wait=False, cancel_futures=True)
            except Exception:
                pass
            
    # Tertiary Fallback: Deterministic ICP Rubric Engine
    return heuristic_icp_qualification(website_text)

def qualify_practice_website(url: str) -> Dict[str, Any]:
    import urllib.request
    from bs4 import BeautifulSoup
    
    if not url.startswith(("http://", "https://")):
        url = "https://" + url
        
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
    }
    
    try:
        req = urllib.request.Request(url, headers=headers)
        with urllib.request.urlopen(req, timeout=12) as resp:
            html = resp.read().decode("utf-8", errors="replace")
        soup = BeautifulSoup(html, "html.parser")
        for tag in soup(["script", "style", "nav", "footer"]):
            tag.decompose()
        text = soup.get_text(separator=" ", strip=True)
        return qualify_practice_text(text)
    except Exception as e:
        return {"status": "FAIL", "reason": f"Website fetch failed: {str(e)[:100]}"}

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Gemini ICP Lead Qualification")
    parser.add_argument("--url", help="URL of practice website to qualify")
    parser.add_argument("--file", help="Path to text file containing website content")
    parser.add_argument("--test", action="store_true", help="Run a verification test on sample practice text")
    args = parser.parse_args()
    
    if args.test:
        sample = """
        Radiance Medical Spa in Charlotte NC. We offer Botox, dermal fillers, Morpheus8 RF microneedling, 
        and BodyTite body contouring. Founded in 2021, our single location in South End provides bespoke 
        aesthetic care for clients across the greater Charlotte area. Book your consultation online today.
        """
        print("Testing qualification on sample boutique med spa...")
        res = qualify_practice_text(sample)
        print("Result:", json.dumps(res, indent=2))
    elif args.url:
        print(f"Qualifying website: {args.url}")
        res = qualify_practice_website(args.url)
        print("Result:", json.dumps(res, indent=2))
    elif args.file:
        with open(args.file, "r", encoding="utf-8") as f:
            content = f.read()
        res = qualify_practice_text(content)
        print("Result:", json.dumps(res, indent=2))
    else:
        parser.print_help()
