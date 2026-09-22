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
import sys
import json
from bs4 import BeautifulSoup
from playwright.async_api import async_playwright

# Add the script dir to sys.path to import gemini_worker
sys.path.append('/home/idrees/job_agent/scripts')
try:
    from gemini_worker import generate_text_with_pool
except ImportError:
    print("Error: Cannot import gemini_worker")
    sys.exit(1)

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

async def process_leads():
    input_file = LEADS_100K
    output_file = LEADS_QUALIFIED
    
    with open(input_file, 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        rows = list(reader)

    print(f"Starting advanced LLM qualification for {len(rows)} leads...")
    results = []

    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        context = await browser.new_context(
            user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/115.0.0.0 Safari/537.36"
        )
        page = await context.new_page()
        
        for idx, row in enumerate(rows):
            website = row.get('Website', '')
            name = row.get('Business Name', f'Lead {idx}')
            
            print(f"\n[{idx+1}/{len(rows)}] Evaluating: {name} ({website})")
            
            try:
                await page.goto(website, wait_until='domcontentloaded', timeout=12000)
                await page.wait_for_timeout(1000)
                content = await page.content()
                soup = BeautifulSoup(content, 'html.parser')
                text = soup.get_text(separator=' ', strip=True)
                
                # Check for an About or Services page if homepage is too short
                if len(text) < 500:
                    for a in soup.find_all('a', href=True):
                        if 'service' in a['href'].lower() or 'about' in a['href'].lower():
                            try:
                                link = a['href']
                                if link.startswith('/'):
                                    link = website.rstrip('/') + link
                                elif not link.startswith('http'):
                                    link = website.rstrip('/') + '/' + link
                                await page.goto(link, wait_until='domcontentloaded', timeout=10000)
                                sub_soup = BeautifulSoup(await page.content(), 'html.parser')
                                text += " " + sub_soup.get_text(separator=' ', strip=True)
                                break
                            except:
                                pass

                if len(text) < 50:
                    print("   -> FAIL: Could not extract enough website text.")
                    continue

                prompt = build_prompt(text)
                llm_response = generate_text_with_pool(prompt)
                
                try:
                    # Clean response if it contains markdown formatting
                    clean_resp = llm_response.replace('```json', '').replace('```', '').strip()
                    decision = json.loads(clean_resp)
                    
                    status = decision.get("status", "FAIL")
                    reason = decision.get("reason", "No reason provided")
                    
                    if status == "PASS":
                        print(f"   -> PASS: {reason[:100]}...")
                        row['ICP_Reason'] = reason
                        results.append(row)
                        
                        # Save incrementally
                        with open(output_file, 'w', newline='', encoding='utf-8') as out_f:
                            writer = csv.DictWriter(out_f, fieldnames=list(row.keys()))
                            writer.writeheader()
                            writer.writerows(results)
                    else:
                        print(f"   -> FAIL: {reason[:100]}...")
                except Exception as e:
                    print(f"   -> LLM Parse Error: {e} | Raw: {llm_response[:50]}")
                    
            except Exception as e:
                print(f"   -> Error accessing website.")

        await browser.close()
        print(f"\nFinished. {len(results)} fully qualified leads saved to {output_file}.")

if __name__ == '__main__':
    asyncio.run(process_leads())
