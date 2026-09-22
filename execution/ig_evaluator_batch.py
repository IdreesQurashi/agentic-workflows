#!/home/idrees/files/Job_Hunting_Archive/job_agent/.venv/bin/python3
import os
import sys
import json
import csv
import re
import time
import random
import requests
import urllib.parse
from bs4 import BeautifulSoup
from playwright.sync_api import sync_playwright

sys.path.append("/home/idrees/Raw various data/job_agent/scripts")
try:
    import gemini_worker
except ImportError:
    print("WARNING: gemini_worker not found.")

def parse_followers(desc):
    if not desc: return 0
    match = re.search(r'([\d\.,]+)([KM]?)\s+Followers', desc, re.IGNORECASE)
    if not match:
        return 0
    num_str = match.group(1).replace(',', '')
    multiplier = match.group(2).upper()
    try:
        val = float(num_str)
        if multiplier == 'K':
            val *= 1000
        elif multiplier == 'M':
            val *= 1000000
        return int(val)
    except:
        return 0

def find_website_ddg(handle):
    url = f"https://html.duckduckgo.com/html/?q={handle}+clinic"
    headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"}
    try:
        resp = requests.get(url, headers=headers, timeout=10)
        soup = BeautifulSoup(resp.text, "html.parser")
        for a in soup.find_all("a", class_="result__url"):
            href = a.get("href")
            if href and "instagram.com" not in href and "facebook.com" not in href and "tiktok.com" not in href and "yelp.com" not in href:
                parsed = urllib.parse.parse_qs(urllib.parse.urlparse(href).query)
                actual_url = parsed.get('uddg', [None])[0]
                if actual_url:
                    return actual_url
    except Exception as e:
        pass
    return None

def scrape_website_text(url, p):
    try:
        browser = p.chromium.launch(headless=True)
        context = browser.new_context(user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64)")
        page = context.new_page()
        page.goto(url, timeout=30000, wait_until="domcontentloaded")
        html = page.content()
        browser.close()
        soup = BeautifulSoup(html, "html.parser")
        return soup.get_text(separator=" ", strip=True)
    except Exception as e:
        print(f"Playwright website rip error: {e}")
        return ""

def evaluate_clinic(text):
    prompt = f"""
    You are evaluating a medical spa / aesthetic clinic website based on strict criteria.
    
    WEBSITE TEXT:
    {text[:15000]}
    
    CRITERIA:
    1. High Ticket Core Offer: Must explicitly offer laser treatments, body sculpting, high-end injectables, or cosmetic surgery. Reject basic facials, haircuts, massages.
    2. Footprint Limit: Operates out of 2 or fewer physical locations.
    3. Public Market Access: Actively markets to the public (not private, celebrity-only, or purely referral-based).
    
    If it fails ANY criteria, output strictly: REJECT
    If it passes ALL criteria, extract their most expensive service and output strictly in JSON format without markdown blocks:
    {{"status": "PASS", "most_expensive_service": "Name of highest ticket service"}}
    """
    try:
        response = gemini_worker.generate_text_with_pool(prompt, model_name="gemini-flash-lite-latest")
        return response.strip()
    except Exception as e:
        print(f"Gemini evaluation error: {e}")
        return "REJECT"

def main():
    input_file = "/home/idrees/Antigravity/Agentic Workflows-20260907T212811Z-1-001/Agentic Workflows/.tmp/instagram_handles.txt"
    output_file = "/home/idrees/Antigravity/Agentic Workflows-20260907T212811Z-1-001/Agentic Workflows/.tmp/validated_clinics.csv"
    
    if not os.path.exists(input_file):
        print(f"Input file not found: {input_file}")
        sys.exit(1)
        
    with open(input_file, "r") as f:
        handles = [line.strip() for line in f if line.strip()]
        
    if not handles:
        print("No more handles to process.")
        sys.exit(0)
    
    batch_size = 100
    batch_handles = handles[:batch_size]
    
    with open(input_file, "w") as f:
        for h in handles[batch_size:]:
            f.write(h + "\n")
            
    print(f"Processing batch of {len(batch_handles)} handles. Remaining: {len(handles)-batch_size}")
    
    file_exists = os.path.exists(output_file)
    with open(output_file, "a", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        if not file_exists:
            writer.writerow(["Handle", "Followers", "URL", "Most Expensive Service"])
        
        with sync_playwright() as p:
            for idx, handle in enumerate(batch_handles):
                print(f"\n[{idx+1}/{len(batch_handles)}] Processing @{handle}")
                try:
                    # User's exact method: open browser, grab html header, instantly close
                    browser = p.chromium.launch(headless=True)
                    context = browser.new_context()
                    page = context.new_page()
                    # only route document to bypass heavy loading
                    page.route("**/*", lambda route: route.continue_() if route.request.resource_type == "document" else route.abort())
                    
                    page.goto(f"https://www.instagram.com/{handle}/", timeout=15000, wait_until="domcontentloaded")
                    html = page.content()
                    browser.close() # IMMEDIATELY CLOSE BROWSER
                    
                    soup = BeautifulSoup(html, "html.parser")
                    # specifically look for og:description
                    meta = soup.find("meta", property="og:description")
                    desc = meta["content"] if meta else ""
                    
                    if not desc:
                        print("  [-] No og:description found on IG. Might be login wall.")
                    else:
                        print(f"  [>] Extracted tag: {desc}")
                        followers = parse_followers(desc)
                        if 1000 <= followers <= 100000:
                            print(f"  [+] Passed audience check: {followers} followers")
                            website_url = find_website_ddg(handle)
                            if website_url:
                                print(f"  [+] Found website: {website_url}")
                                text = scrape_website_text(website_url, p)
                                if text:
                                    result = evaluate_clinic(text)
                                    if "REJECT" in result.upper():
                                        print("  [-] Rejected by Gemini AI Tri-Filter.")
                                    else:
                                        clean_json = re.sub(r'```json\n|\n```|```', '', result).strip()
                                        try:
                                            data = json.loads(clean_json)
                                            if data.get("status") == "PASS":
                                                svc = data.get("most_expensive_service", "Unknown")
                                                print(f"  [!] VALIDATED: Core Offer extracted -> {svc}")
                                                writer.writerow([handle, followers, website_url, svc])
                                                f.flush()
                                        except json.JSONDecodeError:
                                            print("  [-] JSON Decode Error from Gemini.")
                                else:
                                    print("  [-] Could not scrape website text.")
                            else:
                                print("  [-] Could not find website via DDG.")
                        else:
                            print(f"  [-] Failed audience check: {followers} followers")
                            
                except Exception as e:
                    print(f"  [-] Error processing IG: {e}")
                    
                delay = random.uniform(5, 9)
                print(f"  [~] Sleeping for {delay:.1f}s to prevent bans...")
                time.sleep(delay)
                
    print(f"\nBatch complete. Output appended to {output_file}.")

if __name__ == "__main__":
    main()
