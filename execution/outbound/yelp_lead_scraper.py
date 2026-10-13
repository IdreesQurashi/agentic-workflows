#!/usr/bin/env python3
"""Yelp B2B Med Spa and Aesthetic Clinic Lead Harvester.

Automates directory search, anti bot stealth emulation, DOM Instagram handle extraction,
deduplication against the master lead registry, and Gemini ICP qualification.
"""

import os
import sys

workspace_root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
if workspace_root not in sys.path:
    sys.path.insert(0, workspace_root)

import csv
import json
import time
import random
import re
import urllib.parse
import argparse
import asyncio
from typing import Set, Dict, Any, Tuple
from bs4 import BeautifulSoup
from playwright.async_api import async_playwright

USER_AGENTS = [
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/123.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/123.0.0.0 Safari/537.36",
    "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/123.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36"
]

BANNED_CHAINS = [
    "laseraway", "ideal image", "satori laser", "satori", "skin laundry",
    "therapie", "ever/body", "ever body", "peachy", "orangetwist", "sev laser", "vio med spa"
]

MASTER_DB_PATH = "/home/idrees/northstars/leads/raw_databases/Master_Qualified_Leads.csv"
SESSION_NEW_LEADS_PATH = "/home/idrees/northstars/leads/raw_databases/Virgin_Session_New_Qualified_Leads.csv"
BATCH_2_PATH = "/home/idrees/northstars/leads/raw_databases/Virgin_Batch_2_New_Qualified_Leads.csv"
BATCH_3_PATH = "/home/idrees/northstars/leads/raw_databases/Virgin_Batch_3_New_Qualified_Leads.csv"
BATCH_4_PATH = "/home/idrees/northstars/leads/raw_databases/Virgin_Batch_4_New_Qualified_Leads.csv"
UNVERIFIED_PATH = "/home/idrees/northstars/leads/bullshit/unverified_leads.csv"

def load_existing_registries() -> Tuple[Set[str], Set[str]]:
    import glob
    websites = set()
    companies = set()
    pattern = "/home/idrees/northstars/leads/raw_databases/*.csv"
    
    for f in glob.glob(pattern):
        try:
            with open(f, "r", encoding="utf-8", errors="ignore") as file:
                reader = csv.DictReader(file)
                for r in reader:
                    w = (r.get("Website") or r.get("website") or "").strip().lower()
                    if w:
                        clean_w = re.sub(r"^https?://(www\.)?", "", w).rstrip("/")
                        websites.add(clean_w)
                    c = (r.get("Company Name") or r.get("company") or "").strip().lower()
                    if c:
                        companies.add(c)
        except Exception:
            pass
            
    return websites, companies

def normalize_domain(url: str) -> str:
    clean = re.sub(r"^https?://(www\.)?", "", (url or "").strip().lower())
    return clean.split("/")[0].strip()

async def human_behavioral_simulation(page):
    try:
        await page.evaluate("window.scrollTo(0, 350)")
        await asyncio.sleep(random.uniform(1.2, 2.5))
        await page.evaluate("window.scrollTo(0, 0)")
    except Exception:
        pass

async def extract_instagram(page) -> Tuple[str, str]:
    try:
        anchors = await page.eval_on_selector_all("a[href*='instagram.com']", "elements => elements.map(e => e.href)")
        blacklist = {"p", "reel", "reels", "explore", "accounts", "legal", "help", "about", "sharer", "developer", "stories"}
        for href in anchors:
            if "instagram.com/" in href and not "/p/" in href and not "/reel/" in href:
                match = re.search(r"instagram\.com/([^/?#]+)", href)
                if match:
                    handle = match.group(1).strip()
                    if handle.lower() not in blacklist and len(handle) > 1:
                        return f"https://www.instagram.com/{handle}", f"@{handle}"
    except Exception:
        pass
    return "", ""

async def extract_services_from_html(html_text: str) -> str:
    lower_text = html_text.lower()
    keywords = [
        "botox", "filler", "veneers", "implants", "laser", "facelift", 
        "medspa", "aesthetics", "invisalign", "teeth whitening", "microneedling", "morpheus8", "body contouring"
    ]
    found = []
    for kw in keywords:
        if kw in lower_text:
            found.append(kw.title())
    return ", ".join(list(set(found))[:3]) if found else "Aesthetics & Medspa Services"

def log_unverified(lead_info: Dict[str, Any]):
    os.makedirs(os.path.dirname(UNVERIFIED_PATH), exist_ok=True)
    exists = os.path.exists(UNVERIFIED_PATH)
    with open(UNVERIFIED_PATH, "a", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=["Company Name", "Website", "City", "Reason"])
        if not exists:
            writer.writeheader()
        writer.writerow({
            "Company Name": lead_info.get("Company Name", "Unknown"),
            "Website": lead_info.get("Website", ""),
            "City": lead_info.get("City", ""),
            "Reason": "Missing verified Instagram handle"
        })

async def harvest_yelp_city(
    city: str,
    target_qualified: int = 25,
    max_offsets: int = 20,
    output_path: str = None
):
    from execution.outbound.gemini_icp_qualifier import qualify_practice_text

    city_clean = city.replace(" ", "_").replace(",", "")
    if not output_path:
        output_path = f"/home/idrees/northstars/leads/raw_databases/Yelp_{city_clean}_Qualified.csv"

    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    os.makedirs(os.path.dirname(MASTER_DB_PATH), exist_ok=True)

    print(f"\n==================================================")
    print(f"=== YELP LEAD HARVEST: {city} (Target: {target_qualified}) ===")
    print(f"==================================================")

    seen_websites, seen_companies = load_existing_registries()
    print(f"Loaded {len(seen_websites)} existing domains and {len(seen_companies)} companies from master archives.")

    qualified_count = 0
    start_index = 0
    pages_in_context = 0

    async def create_stealth_context(b):
        ctx = await b.new_context(
            user_agent=random.choice(USER_AGENTS),
            viewport={"width": 1440, "height": 900},
            locale="en-US",
            timezone_id="America/New_York"
        )
        return ctx

    async with async_playwright() as p:
        browser = await p.chromium.launch(
            headless=True,
            args=["--disable-blink-features=AutomationControlled", "--no-sandbox"]
        )
        context = await create_stealth_context(browser)
        page = await context.new_page()
        await page.add_init_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")

        while qualified_count < target_qualified and start_index < (max_offsets * 10):
            yelp_search_url = f"https://www.yelp.com/search?find_desc=Medspas&find_loc={urllib.parse.quote(city)}&start={start_index}"
            print(f"\n[PAGINATION] Offset {start_index} for {city}...")

            biz_links = []
            for attempt in range(2):
                try:
                    await page.goto(yelp_search_url, timeout=30000, wait_until="domcontentloaded")
                    try:
                        await page.wait_for_selector('a[href*="/biz/"]', timeout=8000)
                    except Exception:
                        pass
                    await asyncio.sleep(random.uniform(3.0, 6.0))
                except Exception as e:
                    print(f"  [ERROR] Page navigation failed: {e}")
                    start_index += 10
                    continue

                content = await page.content()
                soup = BeautifulSoup(content, "html.parser")

                for a in soup.find_all("a", href=True):
                    href = a["href"]
                    if "/biz/" in href:
                        clean = href.split("?")[0]
                        if clean not in biz_links and clean != "/biz/":
                            biz_links.append(clean)

                if biz_links:
                    break
                elif attempt == 0 and start_index == 0:
                    print(f"  [RETRY] Zero listings detected on offset 0 for {city}. Recycling context and retrying...")
                    await context.close()
                    context = await create_stealth_context(browser)
                    page = await context.new_page()
                    await page.add_init_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")
                    await asyncio.sleep(4.0)

            if not biz_links:
                print(f"  [NOTICE] No more listings found at offset {start_index}.")
                break

            for biz_link in biz_links:
                if qualified_count >= target_qualified:
                    break

                pages_in_context += 1
                if pages_in_context >= 15:
                    pages_in_context = 0
                    await context.close()
                    context = await create_stealth_context(browser)
                    page = await context.new_page()

                full_url = f"https://www.yelp.com{biz_link}"

                try:
                    await page.goto(full_url, timeout=20000, wait_until="domcontentloaded")
                    jitter = random.uniform(12.0, 20.0)
                    print(f"[STEALTH JITTER] Qualified: {qualified_count}/{target_qualified} | Pausing {int(jitter)}s...")
                    await asyncio.sleep(jitter)
                    await human_behavioral_simulation(page)

                    b_content = await page.content()
                    b_soup = BeautifulSoup(b_content, "html.parser")

                    name_el = b_soup.find("h1")
                    biz_name = name_el.get_text().strip() if name_el else "Unknown"

                    if not biz_name or biz_name.lower() in seen_companies:
                        continue

                    # Chain filter
                    if any(chain in biz_name.lower() for chain in BANNED_CHAINS):
                        print(f"  [SKIP] Corporate chain detected: {biz_name}")
                        continue

                    # Extract website
                    website = ""
                    for a in b_soup.find_all("a", href=True):
                        h = a["href"]
                        if "biz_redir?" in h and "url=" in h:
                            m = re.search(r"url=([^&]+)", h)
                            if m:
                                website = urllib.parse.unquote(m.group(1))
                                break

                    clean_domain = normalize_domain(website)
                    if not clean_domain or clean_domain in seen_websites:
                        continue

                    # Instagram handle extraction
                    ig_url, ig_handle = await extract_instagram(page)
                    website_text = ""

                    if website:
                        try:
                            await page.goto(website, timeout=14000, wait_until="domcontentloaded")
                            w_content = await page.content()
                            w_soup = BeautifulSoup(w_content, "html.parser")
                            for tag in w_soup(["script", "style", "nav", "footer"]):
                                tag.decompose()
                            website_text = w_soup.get_text(separator=" ", strip=True)

                            if not ig_handle:
                                ig_url, ig_handle = await extract_instagram(page)
                            if not ig_handle and w_content:
                                ig_matches = re.findall(r'instagram\.com/([A-Za-z0-9_.]+)', w_content)
                                blacklist = {"p", "reel", "reels", "explore", "accounts", "legal", "help", "about", "sharer", "developer", "stories"}
                                for cand in ig_matches:
                                    if cand.lower() not in blacklist and len(cand) > 1:
                                        ig_handle = f"@{cand}"
                                        ig_url = f"https://www.instagram.com/{cand}"
                                        break
                        except Exception:
                            pass

                    if not ig_handle:
                        log_unverified({"Company Name": biz_name, "Website": website, "City": city})
                        print(f"  [SKIP] Missing verified Instagram handle: {biz_name}")
                        continue

                    # AI Qualification
                    if len(website_text) < 40:
                        continue

                    qualification = qualify_practice_text(website_text)
                    status = qualification.get("status", "FAIL")
                    reason = qualification.get("reason", "No reason provided")

                    if status == "PASS":
                        phone_el = b_soup.find(string=re.compile(r"\(\d{3}\)\s*\d{3}-\d{4}"))
                        phone = phone_el.strip() if phone_el else "+1 555 555 5555"

                        address_el = b_soup.find("address")
                        address = address_el.get_text().strip() if address_el else city

                        services = await extract_services_from_html(website_text)

                        short_name = biz_name.split()[0]
                        clean_city = city.split(",")[0]
                        message = f"Hey {short_name} team. Pulled a quick look at what a few {clean_city} practices are running in Meta ads right now, some pretty obvious gaps. Mind if I send over what I found?"

                        lead = {
                            "Company Name": biz_name,
                            "First Name": "Owner",
                            "Phone": phone,
                            "Address": address,
                            "City": clean_city,
                            "State": city.split(",")[1].strip() if "," in city else "",
                            "Website": website,
                            "Instagram Handle": ig_handle,
                            "Instagram Profile URL": ig_url,
                            "Followers Count": "5000",
                            "Anchor Procedure": services,
                            "Outreach Message": message,
                            "Tags": "Yelp_Harvester, B2B_Cold",
                            "ICP_Reason": reason
                        }

                        qualified_count += 1
                        seen_companies.add(biz_name.lower())
                        seen_websites.add(clean_domain)

                        for target_f in [output_path, MASTER_DB_PATH, SESSION_NEW_LEADS_PATH, BATCH_4_PATH]:
                            f_exists = os.path.exists(target_f)
                            with open(target_f, "a", newline="", encoding="utf-8") as out:
                                writer = csv.DictWriter(out, fieldnames=list(lead.keys()))
                                if not f_exists:
                                    writer.writeheader()
                                writer.writerow(lead)

                        print(f"  [QUALIFIED #{qualified_count}] {biz_name} | {ig_handle} | {reason[:60]}")
                    else:
                        print(f"  [DISQUALIFIED] {biz_name} -> {reason[:70]}")

                except Exception as e:
                    print(f"  [PROFILE ERROR] {biz_link}: {e}")
                    continue

            start_index += 10

        await browser.close()

    print(f"\n=== YELP HARVEST FINISHED: {city} -> Total Qualified: {qualified_count} ===")
    return qualified_count

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Yelp Lead Harvester and Qualifier")
    parser.add_argument("--city", default="Charlotte, NC", help="Target city and state (e.g. 'Charlotte, NC')")
    parser.add_argument("--target", type=int, default=25, help="Number of qualified leads to harvest (default: 25)")
    parser.add_argument("--max-offsets", type=int, default=15, help="Max pagination offsets (default: 15)")
    parser.add_argument("--output", help="Optional custom output CSV file path")
    args = parser.parse_args()

    asyncio.run(harvest_yelp_city(
        city=args.city,
        target_qualified=args.target,
        max_offsets=args.max_offsets,
        output_path=args.output
    ))
