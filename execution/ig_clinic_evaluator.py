#!/home/idrees/files/Job_Hunting_Archive/job_agent/.venv/bin/python3
"""
IG Clinic Evaluator
Batch processes Instagram handles through the 4-layer constraint protocol.
"""
import os
import sys
import json
import csv
import re
from apify_client import ApifyClient
from playwright.sync_api import sync_playwright
import bs4

# Make sure we can import gemini_worker
sys.path.append("/home/idrees/files/Job_Hunting_Archive/job_agent/scripts")
try:
    import gemini_worker
except ImportError:
    print("WARNING: gemini_worker not found. AI evaluation will fail.")

APIFY_API_TOKEN = os.getenv("APIFY_API_TOKEN")

def get_ig_profiles_apify(handles):
    """Uses Apify to get IG profiles in batch to extract followers & external url."""
    if not APIFY_API_TOKEN:
        print("Missing APIFY_API_TOKEN in env.")
        sys.exit(1)
        
    client = ApifyClient(APIFY_API_TOKEN)
    # Using a popular, reliable Instagram scraper
    run_input = {
        "usernames": handles,
    }
    print(f"Scraping {len(handles)} IG profiles via Apify to parse followers & bio links...")
    # 'apify/instagram-profile-scraper' is the standard actor
    run = client.actor("apify/instagram-profile-scraper").call(run_input=run_input)
    
    results = []
    for item in client.dataset(run["defaultDatasetId"]).iterate_items():
        results.append(item)
    return results

def scrape_website_text(url):
    """Uses Playwright to rip the full website text."""
    try:
        with sync_playwright() as p:
            browser = p.chromium.launch(headless=True)
            context = browser.new_context(user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/115.0.0.0 Safari/537.36")
            page = context.new_page()
            page.goto(url, timeout=30000, wait_until="domcontentloaded")
            html = page.content()
            browser.close()
            
            soup = bs4.BeautifulSoup(html, "html.parser")
            return soup.get_text(separator=" ", strip=True)
    except Exception as e:
        print(f"Playwright Error for {url}: {e}")
        return ""

def evaluate_clinic(text):
    """Pipes text into Gemini worker pool for qualitative constraints."""
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
        
    # Batch size limit for apify or testing
    # handles = handles[:10]
    
    print(f"Loaded {len(handles)} handles.")
    profiles = get_ig_profiles_apify(handles)
    
    passed_quantitative = []
    
    # 1. Quantitative Filter
    for profile in profiles:
        handle = profile.get("username", "")
        followers = profile.get("followersCount", 0)
        url = profile.get("externalUrl", "")
        
        if 1000 <= followers <= 100000:
            if url:
                passed_quantitative.append({"handle": handle, "followers": followers, "url": url})
            else:
                print(f"[-] {handle} passed follower check but has no website link.")
        else:
            print(f"[-] {handle} rejected (Followers: {followers})")
            
    print(f"\n[+] {len(passed_quantitative)} clinics passed the quantitative audience floor.")
    
    # Write headers if new file
    file_exists = os.path.exists(output_file)
    with open(output_file, "a", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        if not file_exists:
            writer.writerow(["Handle", "Followers", "URL", "Most Expensive Service"])
            
        # 2 & 3. Qualitative Playwright & Gemini Filter
        for idx, clinic in enumerate(passed_quantitative):
            print(f"Evaluating {idx+1}/{len(passed_quantitative)}: {clinic['handle']} ({clinic['url']})")
            text = scrape_website_text(clinic['url'])
            if not text:
                print("   [-] Could not extract website text.")
                continue
                
            result = evaluate_clinic(text)
            
            if "REJECT" in result.upper():
                print("   [-] Rejected by Gemini AI filter.")
                continue
            
            try:
                # Clean JSON if gemini wrapped it in markdown
                clean_json = re.sub(r'```json\n|\n```|```', '', result).strip()
                data = json.loads(clean_json)
                if data.get("status") == "PASS":
                    expensive_service = data.get("most_expensive_service", "Unknown")
                    print(f"   [+] VALIDATED! Core Offer: {expensive_service}")
                    writer.writerow([clinic["handle"], clinic["followers"], clinic["url"], expensive_service])
                    f.flush() # Write immediately to prevent data loss
            except json.JSONDecodeError:
                print(f"   [-] JSON Decode Error. AI Output: {result}")
                
if __name__ == "__main__":
    from dotenv import load_dotenv
    load_dotenv()
    main()
