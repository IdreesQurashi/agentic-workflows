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
    
    reject_words = ['hotel', 'equipment', 'nail salon', 'massage therapist', 'business center', 'resort']
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
You are an expert B2B ICP qualification bot for a high-ticket agency.
Analyze the following website text for an aesthetics/med-spa business.

Strict Requirements to PASS:
1. Locations: The practice must have 2 or fewer physical locations. If they have 3 or more, they FAIL. (If unspecified, assume 1 and PASS).
2. Business Model: They must actively market services to the public. If their website says they are purely 'referral only' or an exclusive 'celebrity word of mouth' closed practice, they FAIL.
3. Core Offer: They must offer high-margin procedures (like laser treatments, body sculpting, injectables, Morpheus8, cosmetic surgery, etc.). If they only offer low-ticket commodities (e.g., basic $50 facials, cheap haircuts, standard massages), they FAIL.

Return your decision in strict JSON format EXACTLY like this:
{{"status": "PASS", "reason": "Explanation here"}}
OR
{{"status": "FAIL", "reason": "Explanation here"}}

Do not include markdown blocks or any other text. Only the raw JSON.

Website Text:
{website_text[:12000]}
"""

async def process():
    input_file = '/home/idrees/Downloads/dataset_google-maps_2026-09-15_15-57-01-038.json'
    output_csv = '/home/idrees/Documents/Final_Leads_Batch_2.csv'
    
    with open(input_file, 'r', encoding='utf-8') as f:
        rows = json.load(f)

    results = []
    qualified_count = 0

    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        context = await browser.new_context(
            user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/115.0.0.0 Safari/537.36"
        )
        page = await context.new_page()
        
        for idx, row in enumerate(rows):
            if not is_valid_icp(row):
                continue
                
            website = row.get('website', '').strip()
            name = row.get('title', f'Lead {idx}')
            
            if not website or 'http' not in website:
                continue
                
            print(f"[{idx+1}/{len(rows)}] Checking: {name}")
            
            ig_url = None
            try:
                await page.goto(website, wait_until='domcontentloaded', timeout=12000)
                content = await page.content()
                soup = BeautifulSoup(content, 'html.parser')
                text = soup.get_text(separator=' ', strip=True)
                
                for a in soup.find_all('a', href=True):
                    href = a.get('href', '')
                    if 'instagram.com/' in href and '/p/' not in href and '/reel/' not in href:
                        ig_url = href
                        break
            except Exception as e:
                pass

            if not ig_url:
                continue
                
            followers = -1
            try:
                await page.goto(ig_url, wait_until='domcontentloaded', timeout=12000)
                await page.wait_for_timeout(1000)
                ig_content = await page.content()
                ig_soup = BeautifulSoup(ig_content, 'html.parser')
                og_desc = ig_soup.find('meta', property='og:description')
                
                if og_desc and og_desc.get('content'):
                    desc = og_desc['content']
                    parts = desc.split('-')[0].split(',')
                    for part in parts:
                        if 'Followers' in part:
                            followers = parse_followers(part.replace('Followers', '').strip())
            except Exception as e:
                pass

            if followers < 0 or followers > 100000:
                print(f"   -> REJECTED: Followers {followers} (Out of 0-100K range)")
                continue
                
            # Now run LLM check
            if len(text) < 500:
                print("   -> FAIL: Not enough website text for LLM.")
                continue

            prompt = build_prompt(text)
            try:
                llm_response = generate_text_with_pool(prompt)
                clean_resp = llm_response.replace('```json', '').replace('```', '').strip()
                decision = json.loads(clean_resp)
                
                status = decision.get("status", "FAIL")
                reason = decision.get("reason", "")
                
                if status == "PASS":
                    print(f"   -> PASS (LLM verified): {reason[:100]}...")
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
                        'ICP_Reason': reason
                    }
                    results.append(row_data)
                    qualified_count += 1
                    
                    with open(output_csv, 'w', newline='', encoding='utf-8') as out_f:
                        writer = csv.DictWriter(out_f, fieldnames=list(row_data.keys()))
                        writer.writeheader()
                        writer.writerows(results)
                        
                    if qualified_count >= 30:
                        print("\nTarget of 30 final qualified leads reached!")
                        break
                else:
                    print(f"   -> REJECTED by LLM: {reason[:80]}...")
            except Exception as e:
                print(f"   -> LLM Error: {e}")

        await browser.close()
        print(f"\nDone. Extracted {qualified_count} leads to {output_csv}")

if __name__ == '__main__':
    asyncio.run(process())
