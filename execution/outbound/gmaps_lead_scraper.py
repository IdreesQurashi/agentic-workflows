#!/usr/bin/env python3
"""Google Maps B2B Lead Harvester and ICP Qualifier.

Searches Google Maps for aesthetics, med spas, and cosmetic practices using
headless Playwright. Extracts listings, crawls websites for Instagram handles,
checks deduplication against master records, and runs Gemini ICP qualification.
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
from typing import Set, Dict, Any, Tuple, List
from bs4 import BeautifulSoup
from playwright.async_api import async_playwright

USER_AGENTS = [
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.3 Safari/605.1.15",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:123.0) Gecko/20100101 Firefox/123.0"
]

BANNED_CHAINS = [
    "laseraway", "ideal image", "satori laser", "satori", "skin laundry",
    "therapie", "ever/body", "ever body", "peachy", "orangetwist", "sev laser", "vio med spa"
]

MASTER_DB_PATH = "/home/idrees/northstars/leads/raw_databases/Master_Qualified_Leads.csv"
SESSION_NEW_LEADS_PATH = "/home/idrees/northstars/leads/raw_databases/Virgin_Session_New_Qualified_Leads.csv"
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

async def extract_instagram_from_html(html_text: str) -> Tuple[str, str]:
    soup = BeautifulSoup(html_text, "html.parser")
    blacklist = {"p", "reel", "reels", "explore", "accounts", "legal", "help", "about", "sharer", "developer", "stories"}
    
    for a in soup.find_all("a", href=True):
        href = a["href"]
        if "instagram.com/" in href and not "/p/" in href and not "/reel/" in href:
            match = re.search(r"instagram\.com/([^/?#]+)", href)
            if match:
                handle = match.group(1).strip()
                if handle.lower() not in blacklist and len(handle) > 1:
                    return f"https://www.instagram.com/{handle}", f"@{handle}"
                    
    match = re.search(r"https?://(?:www\.)?instagram\.com/([A-Za-z0-9_.]+)", html_text)
    if match:
        h = match.group(1).strip()
        if h.lower() not in blacklist and len(h) > 1:
            return f"https://www.instagram.com/{h}", f"@{h}"
            
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

async def harvest_gmaps_city(
    city: str,
    query: str = None,
    target_qualified: int = 25,
    max_scrolls: int = 20,
    output_path: str = None
):
    from execution.outbound.gemini_icp_qualifier import qualify_practice_text

    search_query = query if query else f"Med Spas in {city}"
    city_clean = city.replace(" ", "_").replace(",", "")
    if not output_path:
        output_path = f"/home/idrees/northstars/leads/raw_databases/Gmaps_{city_clean}_Qualified.csv"

    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    os.makedirs(os.path.dirname(MASTER_DB_PATH), exist_ok=True)

    print(f"\n==================================================")
    print(f"=== GOOGLE MAPS HARVEST: {search_query} (Target: {target_qualified}) ===")
    print(f"==================================================")

    seen_websites, seen_companies = load_existing_registries()
    print(f"Loaded {len(seen_websites)} existing domains and {len(seen_companies)} companies.")

    qualified_count = 0

    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        context = await browser.new_context(user_agent=random.choice(USER_AGENTS))
        page = await context.new_page()

        maps_url = f"https://www.google.com/maps/search/{urllib.parse.quote(search_query)}"
        print(f"Navigating to Google Maps: {maps_url}...")
        
        try:
            await page.goto(maps_url, timeout=35000, wait_until="domcontentloaded")
            await asyncio.sleep(5.0)
        except Exception as e:
            print(f"Failed to load Google Maps: {e}")
            await browser.close()
            return 0

        # Scroll feed container to load listings
        feed_selector = "div[role='feed']"
        try:
            await page.wait_for_selector(feed_selector, timeout=10000)
        except Exception:
            print("Listing feed selector not found. Retrying page content directly...")

        for s in range(max_scrolls):
            try:
                await page.evaluate(f"""
                    const feed = document.querySelector("{feed_selector}");
                    if (feed) feed.scrollTop = feed.scrollHeight;
                """)
                await asyncio.sleep(random.uniform(2.0, 3.5))
            except Exception:
                break

        # Parse listings
        content = await page.content()
        soup = BeautifulSoup(content, "html.parser")
        
        cards = soup.find_all("div", attrs={"jsaction": True})
        candidate_links = []
        for a in soup.find_all("a", href=True):
            href = a["href"]
            if "/maps/place/" in href:
                clean_href = href.split("?")[0]
                if clean_href not in candidate_links:
                    candidate_links.append(clean_href)

        print(f"Found {len(candidate_links)} Google Maps candidate listings.")

        for place_url in candidate_links:
            if qualified_count >= target_qualified:
                break

            try:
                await page.goto(place_url, timeout=20000, wait_until="domcontentloaded")
                await asyncio.sleep(random.uniform(3.0, 5.0))
                p_content = await page.content()
                p_soup = BeautifulSoup(p_content, "html.parser")

                name_el = p_soup.find("h1")
                biz_name = name_el.get_text().strip() if name_el else "Unknown"

                if not biz_name or biz_name.lower() in seen_companies:
                    continue

                if any(chain in biz_name.lower() for chain in BANNED_CHAINS):
                    print(f"  [SKIP] Corporate chain: {biz_name}")
                    continue

                # Website
                website = ""
                for a in p_soup.find_all("a", href=True):
                    aria = a.get("aria-label", "").lower()
                    h = a["href"]
                    if "website" in aria or "authority" in a.get("data-item-id", ""):
                        website = h
                        break
                    if "http" in h and "google.com" not in h and "gstatic.com" not in h:
                        website = h
                        break

                clean_domain = normalize_domain(website)
                if not clean_domain or clean_domain in seen_websites:
                    continue

                # Crawl website for Instagram and Services
                ig_url, ig_handle = "", ""
                website_text = ""

                try:
                    await page.goto(website, timeout=14000, wait_until="domcontentloaded")
                    w_content = await page.content()
                    w_soup = BeautifulSoup(w_content, "html.parser")
                    for tag in w_soup(["script", "style", "nav", "footer"]):
                        tag.decompose()
                    website_text = w_soup.get_text(separator=" ", strip=True)
                    ig_url, ig_handle = await extract_instagram_from_html(w_content)
                except Exception:
                    pass

                if not ig_handle:
                    log_unverified({"Company Name": biz_name, "Website": website, "City": city})
                    print(f"  [SKIP] No verified Instagram handle: {biz_name}")
                    continue

                if len(website_text) < 40:
                    continue

                # Gemini ICP Qualification
                qualification = qualify_practice_text(website_text)
                status = qualification.get("status", "FAIL")
                reason = qualification.get("reason", "No reason provided")

                if status == "PASS":
                    services = await extract_services_from_html(website_text)
                    short_name = biz_name.split()[0]
                    clean_city = city.split(",")[0]
                    message = f"Hey {short_name} team. Pulled a quick look at what a few {clean_city} practices are running in Meta ads right now, some pretty obvious gaps. Mind if I send over what I found?"

                    lead = {
                        "Company Name": biz_name,
                        "First Name": "Owner",
                        "Phone": "+1 555 555 5555",
                        "Address": city,
                        "City": clean_city,
                        "State": city.split(",")[1].strip() if "," in city else "",
                        "Website": website,
                        "Instagram Handle": ig_handle,
                        "Instagram Profile URL": ig_url,
                        "Followers Count": "5000",
                        "Anchor Procedure": services,
                        "Outreach Message": message,
                        "Tags": "GoogleMaps_Harvester, B2B_Cold",
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
                print(f"  [LISTING ERROR]: {e}")
                continue

        await browser.close()

    print(f"\n=== GOOGLE MAPS HARVEST FINISHED: {city} -> Total Qualified: {qualified_count} ===")
    return qualified_count

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Google Maps B2B Harvester")
    parser.add_argument("--city", default="Charlotte, NC", help="Target city and state")
    parser.add_argument("--query", help="Custom search query override")
    parser.add_argument("--target", type=int, default=25, help="Target qualified leads")
    parser.add_argument("--scrolls", type=int, default=15, help="Number of scrolls down listing feed")
    parser.add_argument("--output", help="Custom output CSV path")
    args = parser.parse_args()

    asyncio.run(harvest_gmaps_city(
        city=args.city,
        query=args.query,
        target_qualified=args.target,
        max_scrolls=args.scrolls,
        output_path=args.output
    ))
