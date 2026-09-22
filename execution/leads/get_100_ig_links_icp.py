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
from bs4 import BeautifulSoup
from playwright.async_api import async_playwright

def is_valid_icp(place):
    category = place.get('categoryName', '').lower()
    title = place.get('title', '').lower()
    
    # Reject completely irrelevant categories
    reject_words = ['hotel', 'equipment', 'nail salon', 'massage therapist', 'business center', 'resort']
    for rw in reject_words:
        if rw in category or rw in title:
            return False
            
    # Accept ICP keywords
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

async def process_businesses():
    input_file = '/home/idrees/Downloads/dataset_google-maps_2026-09-15_15-02-10-408.json'
    output_csv = str(LEADS_100_IG)
    
    with open(input_file, 'r', encoding='utf-8') as f:
        rows = json.load(f)

    results = []
    found_count = 0

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
                
            print(f"[{idx+1}/{len(rows)}] ICP Matched: {name}")
            
            ig_url = None
            try:
                await page.goto(website, wait_until='domcontentloaded', timeout=12000)
                content = await page.content()
                soup = BeautifulSoup(content, 'html.parser')
                
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

            row_data = {
                'Business Name': name,
                'Category': row.get('categoryName', ''),
                'Website': website,
                'Instagram': ig_url,
                'Followers': followers,
                'Phone': row.get('phone', ''),
                'Address': row.get('address', ''),
                'Score': row.get('totalScore', ''),
                'Reviews': row.get('reviewsCount', '')
            }
            results.append(row_data)
            found_count += 1
            
            print(f"   -> Found IG {found_count}/100: {ig_url} | Followers: {followers}")
            
            with open(output_csv, 'w', newline='', encoding='utf-8') as out_f:
                writer = csv.DictWriter(out_f, fieldnames=row_data.keys())
                writer.writeheader()
                writer.writerows(results)
                
            if found_count >= 100:
                print("\nTarget of 100 ICP Instagram links reached.")
                break

        await browser.close()

if __name__ == '__main__':
    asyncio.run(process_businesses())
