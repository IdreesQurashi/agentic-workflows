import sys
from pathlib import Path
EXECUTION_DIR = Path(__file__).resolve().parent.parent
if str(EXECUTION_DIR) not in sys.path:
    sys.path.insert(0, str(EXECUTION_DIR))
from _root import DATA_LEADS_DIR, LEADS_100K, LEADS_100_IG, LEADS_QUALIFIED, LEADS_FILTERED, URLS_FILE, LEADS_DB, ENV_FILE
from dotenv import load_dotenv
load_dotenv(ENV_FILE)
import asyncio
import json
import csv
import sys
import random
import os
from bs4 import BeautifulSoup
from playwright.async_api import async_playwright

sys.path.append('/home/idrees/job_agent/scripts')
try:
    from gemini_worker import generate_text_with_pool
except ImportError:
    print("Error: Cannot import gemini_worker")
    sys.exit(1)

def is_valid_icp(place):
    category = place.get('categoryName', '').lower()
    title = place.get('title', '').lower()
    reject_words = ['hotel', 'equipment', 'nail salon', 'massage therapist', 'business center', 'resort', 'supply', 'academy', 'school']
    for rw in reject_words:
        if rw in category or rw in title:
            return False
    accept_words = ['spa', 'skin', 'laser', 'clinic', 'dentist', 'dental', 'aesthetic', 'esthetic', 'medical', 'wellness', 'beauty', 'surgeon', 'plastic']
    for aw in accept_words:
        if aw in category or aw in title:
            return True
    return False

def parse_followers(text):
    text = text.strip().upper()
    multiplier = 1
    if text.endswith('K'):
        multiplier = 1000
        text = text[:-1]
    elif text.endswith('M'):
        multiplier = 1000000
        text = text[:-1]
    try:
        return int(float(text.replace(',', '')) * multiplier)
    except:
        return 0

def build_prompt(website_text):
    return f"""
You are an expert B2B ICP qualification bot. Analyze this website text for an aesthetics/med-spa business.
Strict Requirements to PASS:
1. Locations: 2 or fewer physical locations.
2. Business Model: Actively markets services to the public (no 'referral only'/'celebrity only').
3. Core Offer: High-margin procedures (laser treatments, body sculpting, injectables, cosmetic surgery). No purely low-ticket commodities (basic facials, haircuts, standard massage).
Return JSON EXACTLY like: {{"status": "PASS", "reason": "..."}} OR {{"status": "FAIL", "reason": "..."}}
Website Text:
{website_text[:12000]}
"""

async def process():
    input_file = '/home/idrees/Downloads/dataset_google-maps_2026-09-16_05-55-07-165.json'
    output_csv = '/home/idrees/northstars/leads/daily leads database/Recovered_Leads_1K_Floor.csv'
    
    with open(input_file, 'r', encoding='utf-8') as f:
        rows = json.load(f)

    start_index = 1715
    print(f"Resuming recovery from row {start_index} to {len(rows)} with 1000 to 100,000 baseline...")
    file_exists = os.path.isfile(output_csv)

    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        context = await browser.new_context(
            user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/115.0.0.0 Safari/537.36"
        )
        page = await context.new_page()
        
        for idx in range(start_index, len(rows)):
            row = rows[idx]
            if not is_valid_icp(row):
                continue
                
            website = row.get('website', '').strip()
            name = row.get('title', f'Lead {idx}')
            if not website or 'http' not in website:
                continue
                
            ig_url = None
            try:
                await page.goto(website, wait_until='domcontentloaded', timeout=15000)
                content = await page.content()
                soup = BeautifulSoup(content, 'html.parser')
                text = soup.get_text(separator=' ', strip=True)
                for a in soup.find_all('a', href=True):
                    href = a.get('href', '')
                    if 'instagram.com/' in href and '/p/' not in href and '/reel/' not in href:
                        ig_url = href
                        break
            except Exception:
                pass

            if not ig_url:
                continue
                
            delay = random.uniform(5.0, 9.0)
            await asyncio.sleep(delay)
            
            followers = -1
            try:
                await page.goto(ig_url, wait_until='domcontentloaded', timeout=12000)
                ig_content = await page.content()
                ig_soup = BeautifulSoup(ig_content, 'html.parser')
                og_desc = ig_soup.find('meta', property='og:description')
                if og_desc and og_desc.get('content'):
                    desc = og_desc['content']
                    for part in desc.split('-')[0].split(','):
                        if 'Followers' in part:
                            followers = parse_followers(part.replace('Followers', '').strip())
            except Exception:
                pass

            if followers < 1000 or followers > 100000:
                continue
                
            if len(text) < 500:
                continue

            prompt = build_prompt(text)
            try:
                llm_response = generate_text_with_pool(prompt)
                clean_resp = llm_response.replace('```json', '').replace('```', '').strip()
                decision = json.loads(clean_resp)
                
                if decision.get("status", "FAIL") == "PASS":
                    row_data = {
                        'Business Name': name,
                        'Category': row.get('categoryName', ''),
                        'Website': website,
                        'Instagram': ig_url,
                        'Followers': followers,
                        'Phone': row.get('phone', ''),
                        'Address': row.get('address', ''),
                        'Score': row.get('totalScore', ''),
                        'Reviews': row.get('reviewsCount', ''),
                        'ICP_Reason': decision.get('reason', '')
                    }
                    
                    with open(output_csv, 'a', newline='', encoding='utf-8') as out_f:
                        writer = csv.DictWriter(out_f, fieldnames=list(row_data.keys()))
                        if not file_exists:
                            writer.writeheader()
                            file_exists = True
                        writer.writerow(row_data)
                        print(f"Recovered: {name} ({followers} Followers)")
            except Exception:
                pass

        await browser.close()
        print("\nFinal recovery sweep completely finished.")

if __name__ == '__main__':
    asyncio.run(process())
