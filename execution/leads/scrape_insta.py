import sys
from pathlib import Path
EXECUTION_DIR = Path(__file__).resolve().parent.parent
if str(EXECUTION_DIR) not in sys.path:
    sys.path.insert(0, str(EXECUTION_DIR))
from _root import DATA_LEADS_DIR, LEADS_100K, LEADS_100_IG, LEADS_QUALIFIED, LEADS_FILTERED, URLS_FILE, LEADS_DB, ENV_FILE
from dotenv import load_dotenv
load_dotenv(ENV_FILE)
import asyncio
import re
import csv
from bs4 import BeautifulSoup
from playwright.async_api import async_playwright

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

async def process_urls(urls):
    results = []
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        # Reuse context to maybe avoid quick blocks
        context = await browser.new_context(
            user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/115.0.0.0 Safari/537.36"
        )
        page = await context.new_page()
        
        for idx, url in enumerate(urls):
            try:
                print(f"Scraping [{idx+1}/{len(urls)}]: {url}")
                await page.goto(url, wait_until='domcontentloaded')
                await page.wait_for_timeout(1500) # give it a moment
                content = await page.content()
                
                soup = BeautifulSoup(content, 'html.parser')
                og_desc = soup.find('meta', property='og:description')
                
                if og_desc and og_desc.get('content'):
                    desc = og_desc['content']
                    # e.g., "40K Followers, 1,004 Following, 929 Posts - ..."
                    parts = desc.split('-')[0].split(',')
                    followers = -1
                    posts = -1
                    for part in parts:
                        part = part.strip()
                        if 'Followers' in part:
                            followers = parse_followers(part.replace('Followers', '').strip())
                        if 'Posts' in part:
                            posts = parse_followers(part.replace('Posts', '').strip())
                    
                    if followers >= 0:
                        print(f"   Found: {followers} followers")
                        results.append({
                            'url': url,
                            'followers': followers,
                            'posts': posts,
                            'status': 'success' if followers >= 0 else 'no_data'
                        })
                    else:
                        print(f"   No follower count found.")
                else:
                    print(f"   No og:description found.")
            except Exception as e:
                print(f"   Error: {e}")
            
            await page.wait_for_timeout(1000) # delay to avoid rate limit
        await browser.close()
    return results

def main():
    with open(URLS_FILE, 'r') as f:
        urls = [line.strip() for line in f if line.strip()]
    
    results = asyncio.run(process_urls(urls))
    
    filtered = [r for r in results if r.get('followers', 0) >= 5000]
    
    with open(LEADS_FILTERED, 'w', newline='', encoding='utf-8') as f:
        writer = csv.DictWriter(f, fieldnames=['url', 'followers', 'posts', 'status'])
        writer.writeheader()
        for r in filtered:
            writer.writerow(r)
            
    print(f"\nDone. Saved {len(filtered)} valid profiles to filtered_instagrams.csv.")

if __name__ == '__main__':
    main()
