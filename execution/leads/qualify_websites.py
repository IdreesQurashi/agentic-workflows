import sys
from pathlib import Path
EXECUTION_DIR = Path(__file__).resolve().parent.parent
if str(EXECUTION_DIR) not in sys.path:
    sys.path.insert(0, str(EXECUTION_DIR))
from _root import DATA_LEADS_DIR, LEADS_100K, LEADS_100_IG, LEADS_QUALIFIED, LEADS_FILTERED, URLS_FILE, LEADS_DB, ENV_FILE
from dotenv import load_dotenv
load_dotenv(ENV_FILE)
import asyncio
import csv
from bs4 import BeautifulSoup
from playwright.async_api import async_playwright
import urllib.parse

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

async def process_businesses(input_csv, output_csv):
    results = []
    
    with open(input_csv, 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        rows = list(reader)

    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        context = await browser.new_context(
            user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/115.0.0.0 Safari/537.36"
        )
        page = await context.new_page()
        
        qualified_count = 0

        for idx, row in enumerate(rows):
            website = row.get('website', '').strip()
            name = row.get('title', row.get('name', f'Lead {idx}'))
            
            if not website or 'http' not in website:
                continue
                
            print(f"[{idx+1}/{len(rows)}] Checking {name} : {website}")
            
            ig_url = None
            try:
                await page.goto(website, wait_until='domcontentloaded', timeout=15000)
                content = await page.content()
                soup = BeautifulSoup(content, 'html.parser')
                
                for a in soup.find_all('a', href=True):
                    href = a['href']
                    if 'instagram.com/' in href and '/p/' not in href and '/reel/' not in href:
                        ig_url = href
                        break
            except Exception as e:
                print(f"   Failed to load website.")
                continue

            if not ig_url:
                print("   No Instagram found.")
                continue
                
            print(f"   Found IG: {ig_url}")
            
            try:
                await page.goto(ig_url, wait_until='domcontentloaded', timeout=15000)
                await page.wait_for_timeout(1500)
                ig_content = await page.content()
                ig_soup = BeautifulSoup(ig_content, 'html.parser')
                og_desc = ig_soup.find('meta', property='og:description')
                
                if og_desc and og_desc.get('content'):
                    desc = og_desc['content']
                    parts = desc.split('-')[0].split(',')
                    followers = -1
                    
                    for part in parts:
                        if 'Followers' in part:
                            followers = parse_followers(part.replace('Followers', '').strip())
                    
                    if followers >= 5000:
                        print(f"   QUALIFIED: {followers} followers")
                        row['instagram_url'] = ig_url
                        row['followers'] = followers
                        results.append(row)
                        qualified_count += 1
                        
                        # Save incrementally
                        with open(output_csv, 'w', newline='', encoding='utf-8') as out_f:
                            writer = csv.DictWriter(out_f, fieldnames=list(row.keys()))
                            writer.writeheader()
                            writer.writerows(results)
                    else:
                        print(f"   Unqualified: {followers} followers")
            except Exception as e:
                print(f"   IG Scrape Failed.")
                
            if qualified_count >= 75:
                print("Target reached. Halting extraction.")
                break

        await browser.close()
    return results

if __name__ == '__main__':
    # Expects Apify export to be named raw_apify.csv
    asyncio.run(process_businesses(str(DATA_LEADS_DIR / 'raw_apify.csv'), str(DATA_LEADS_DIR / 'qualified_leads.csv')))
