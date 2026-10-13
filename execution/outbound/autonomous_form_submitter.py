#!/usr/bin/env python3
"""Autonomous Clinic Contact Form Submitter.

CMS-agnostic form submission engine utilizing headless Playwright with stealth evasion,
human keystroke jitter, honeypot field avoidance, captcha detection gating,
and persistent submission logging.
"""

import os
import sys
import re
import csv
import time
import random
import asyncio
import argparse
import urllib.parse
from datetime import datetime
from typing import Dict, List, Optional, Tuple, Any

from playwright.async_api import async_playwright, Page, ElementHandle, BrowserContext

LOG_CSV_PATH = "/home/idrees/northstars/leads/form_submissions_log.csv"
SCREENSHOTS_DIR = "/home/idrees/Antigravity/Agentic Workflows-20260907T212811Z-1-001/Agentic Workflows/reports/screenshots"

DEFAULT_SENDER = {
    "first_name": "Idrees",
    "last_name": "Qurashi",
    "full_name": "Idrees Qurashi",
    "email": "idrees@northstarsmb.com",
    "phone": "5125550199",
    "company": "Northstars Lab"
}

USER_AGENTS = [
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/123.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:125.0) Gecko/20100101 Firefox/125.0",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.4.1 Safari/605.1.15"
]

def load_contacted_domains() -> set:
    seen = set()
    if os.path.exists(LOG_CSV_PATH):
        try:
            with open(LOG_CSV_PATH, mode="r", encoding="utf-8-sig") as f:
                reader = csv.DictReader(f)
                for row in reader:
                    domain = row.get("domain", "").strip().lower()
                    status = row.get("status", "").strip().upper()
                    if domain and status in ("SUCCESS", "SKIPPED_CAPTCHA", "SUBMITTED"):
                        seen.add(domain)
        except Exception:
            pass
    return seen

def log_submission_result(
    clinic_name: str,
    domain: str,
    url: str,
    status: str,
    mode: str,
    details: str,
    screenshot_path: str = ""
):
    os.makedirs(os.path.dirname(LOG_CSV_PATH), exist_ok=True)
    file_exists = os.path.exists(LOG_CSV_PATH)
    fieldnames = [
        "timestamp", "clinic_name", "domain", "url",
        "status", "mode", "details", "screenshot_path"
    ]
    with open(LOG_CSV_PATH, mode="a", encoding="utf-8-sig", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        if not file_exists:
            writer.writeheader()
        writer.writerow({
            "timestamp": datetime.now().isoformat(),
            "clinic_name": clinic_name,
            "domain": domain,
            "url": url,
            "status": status,
            "mode": mode,
            "details": details,
            "screenshot_path": screenshot_path
        })

def normalize_domain(url: str) -> str:
    try:
        parsed = urllib.parse.urlparse(url)
        netloc = parsed.netloc or parsed.path
        return netloc.replace("www.", "").lower().split(":")[0]
    except Exception:
        return url.lower()

def craft_form_message(clinic_name: str, city: str) -> str:
    clean_name = clinic_name.strip() if clinic_name and clinic_name.lower() != "clinic" else "your"
    clean_city = city.strip() if city else "your local area"
    return (
        f"Hi {clean_name} team,\n\n"
        f"I work with aesthetic clinics in {clean_city} on patient acquisition infrastructure. "
        f"Noticed a few clear leaks in how high-ticket cosmetic inquiries are being captured and converted "
        f"compared to competing practices in your area.\n\n"
        f"We build patient booking pipelines specifically for established medspas. "
        f"Would you be opposed to a brief 10-minute strategy call with our founder Muaaz next week to see what we found?\n\n"
        f"Best,\n"
        f"Idrees Qurashi\n"
        f"Northstars Lab\n"
        f"idrees@northstarsmb.com"
    )

async def check_for_captcha(page: Page) -> Tuple[bool, str]:
    captcha_selectors = [
        "iframe[src*='recaptcha']",
        "iframe[src*='hcaptcha']",
        "iframe[src*='turnstile']",
        ".g-recaptcha",
        ".h-captcha",
        ".cf-turnstile",
        "div[data-sitekey]",
        "#g-recaptcha"
    ]
    for sel in captcha_selectors:
        try:
            elem = await page.query_selector(sel)
            if elem and await elem.is_visible():
                return True, f"Detected active captcha matching selector: {sel}"
        except Exception:
            continue
    return False, ""

async def is_honeypot(input_elem: ElementHandle) -> bool:
    try:
        is_visible = await input_elem.is_visible()
        if not is_visible:
            return True
        box = await input_elem.bounding_box()
        if not box or box["width"] <= 1 or box["height"] <= 1:
            return True
        html_snippet = await input_elem.evaluate(
            "el => (el.name + ' ' + el.id + ' ' + el.className).toLowerCase()"
        )
        for flag in ["honeypot", "hp-field", "antispam", "leave_blank", "trap"]:
            if flag in html_snippet:
                return True
        return False
    except Exception:
        return False

async def human_type(element: ElementHandle, text: str):
    await element.click()
    await asyncio.sleep(random.uniform(0.1, 0.3))
    await element.evaluate("el => el.value = ''")
    for char in text:
        await element.type(char, delay=random.randint(25, 75))
    await asyncio.sleep(random.uniform(0.15, 0.4))

async def find_contact_url(context: BrowserContext, base_url: str) -> Optional[str]:
    page = await context.new_page()
    try:
        await page.goto(base_url, timeout=15000, wait_until="domcontentloaded")
        await asyncio.sleep(1)

        parsed = urllib.parse.urlparse(base_url)
        origin = f"{parsed.scheme}://{parsed.netloc}"
        candidates = [
            f"{origin}/contact",
            f"{origin}/contact-us",
            f"{origin}/contact/",
            f"{origin}/contact-us/",
            f"{origin}/get-in-touch",
            f"{origin}/consultation",
            base_url
        ]
        
        links = await page.query_selector_all("a[href]")
        for link in links:
            href = await link.get_attribute("href")
            text = (await link.inner_text()).lower() if href else ""
            if href and any(k in text for k in ["contact", "get in touch", "consultation", "reach us"]):
                full_href = urllib.parse.urljoin(base_url, href)
                if parsed.netloc in full_href and full_href not in candidates:
                    candidates.insert(0, full_href)

        await page.close()

        for candidate in candidates:
            test_page = await context.new_page()
            try:
                resp = await test_page.goto(candidate, timeout=12000, wait_until="domcontentloaded")
                if resp and resp.status == 200:
                    form = await test_page.query_selector("form textarea, form input[type='email']")
                    if form:
                        await test_page.close()
                        return candidate
            except Exception:
                pass
            finally:
                if not test_page.is_closed():
                    await test_page.close()
        return base_url
    except Exception:
        if not page.is_closed():
            await page.close()
        return base_url

async def process_clinic_form(
    context: BrowserContext,
    clinic_name: str,
    city: str,
    website_url: str,
    dry_run: bool = True
) -> Dict[str, Any]:
    domain = normalize_domain(website_url)
    os.makedirs(SCREENSHOTS_DIR, exist_ok=True)
    
    print(f"\n[+] Processing: {clinic_name} ({domain})")
    target_url = await find_contact_url(context, website_url)
    print(f"    Target URL: {target_url}")
    
    page = await context.new_page()
    await page.set_viewport_size({
        "width": random.choice([1366, 1440, 1920]),
        "height": random.choice([768, 900, 1080])
    })

    try:
        resp = await page.goto(target_url, timeout=20000, wait_until="domcontentloaded")
        await asyncio.sleep(2)
        
        await page.evaluate("window.scrollBy(0, 400);")
        await asyncio.sleep(random.uniform(0.8, 1.5))
        await page.evaluate("window.scrollBy(0, -200);")
        await asyncio.sleep(random.uniform(0.5, 1.0))

        # 1. Check for Captcha
        has_captcha, captcha_msg = await check_for_captcha(page)
        if has_captcha:
            screenshot_path = os.path.join(SCREENSHOTS_DIR, f"captcha_{domain}_{int(time.time())}.png")
            await page.screenshot(path=screenshot_path)
            log_submission_result(clinic_name, domain, target_url, "SKIPPED_CAPTCHA", "DRY_RUN" if dry_run else "LIVE", captcha_msg, screenshot_path)
            print(f"    [!] {captcha_msg}. Skipping to avoid detection.")
            await page.close()
            return {"status": "SKIPPED_CAPTCHA", "reason": captcha_msg}

        # 2. Locate Contact Form
        forms = await page.query_selector_all("form")
        best_form = None
        for form in forms:
            has_textarea = await form.query_selector("textarea")
            has_email = await form.query_selector("input[type='email'], input[name*='email' i]")
            if has_textarea or has_email:
                best_form = form
                break

        if not best_form:
            log_submission_result(clinic_name, domain, target_url, "NO_FORM_FOUND", "DRY_RUN" if dry_run else "LIVE", "No usable contact form found on page")
            print("    [-] No usable contact form found.")
            await page.close()
            return {"status": "NO_FORM_FOUND"}

        # 3. Detect and Map Fields
        inputs = await best_form.query_selector_all("input:not([type='hidden']):not([type='submit']):not([type='button']), textarea")
        fields_filled = []

        message_text = craft_form_message(clinic_name, city)

        for inp in inputs:
            if await is_honeypot(inp):
                continue

            inp_type = (await inp.get_attribute("type") or "text").lower()
            tag_name = await inp.evaluate("el => el.tagName.toLowerCase()")
            meta_str = await inp.evaluate("el => (el.name + ' ' + el.id + ' ' + (el.placeholder || '') + ' ' + (el.getAttribute('aria-label') || '')).toLowerCase()")

            if tag_name == "textarea" or "message" in meta_str or "comment" in meta_str or "inquiry" in meta_str:
                await human_type(inp, message_text)
                fields_filled.append("message")
                continue

            if inp_type == "email" or "email" in meta_str:
                await human_type(inp, DEFAULT_SENDER["email"])
                fields_filled.append("email")
                continue

            if inp_type == "tel" or "phone" in meta_str or "cell" in meta_str or "mobile" in meta_str:
                await human_type(inp, DEFAULT_SENDER["phone"])
                fields_filled.append("phone")
                continue

            if "first" in meta_str:
                await human_type(inp, DEFAULT_SENDER["first_name"])
                fields_filled.append("first_name")
                continue

            if "last" in meta_str:
                await human_type(inp, DEFAULT_SENDER["last_name"])
                fields_filled.append("last_name")
                continue

            if "name" in meta_str:
                await human_type(inp, DEFAULT_SENDER["full_name"])
                fields_filled.append("full_name")
                continue

            if "subject" in meta_str or "topic" in meta_str:
                await human_type(inp, f"Question regarding {clinic_name}")
                fields_filled.append("subject")
                continue

        checkboxes = await best_form.query_selector_all("input[type='checkbox']")
        for cb in checkboxes:
            try:
                cb_label = await cb.evaluate("el => (el.name + ' ' + el.id + ' ' + (el.parentElement ? el.parentElement.innerText : '')).toLowerCase()")
                if any(k in cb_label for k in ["agree", "terms", "consent", "privacy", "opt-in", "policy"]):
                    is_checked = await cb.is_checked()
                    if not is_checked:
                        await cb.click()
                        fields_filled.append("consent_checkbox")
            except Exception:
                pass

        print(f"    [+] Filled fields: {', '.join(set(fields_filled))}")

        timestamp_int = int(time.time())
        mode_str = "dryrun" if dry_run else "live"
        screenshot_path = os.path.join(SCREENSHOTS_DIR, f"{mode_str}_{domain}_{timestamp_int}.png")
        await page.screenshot(path=screenshot_path)
        print(f"    [+] Saved form screenshot to: {screenshot_path}")

        if dry_run:
            log_submission_result(clinic_name, domain, target_url, "DRY_RUN_READY", "DRY_RUN", f"Fields filled: {','.join(fields_filled)}", screenshot_path)
            print("    [✓] Dry run complete. Form filled cleanly without clicking submit.")
            await page.close()
            return {"status": "DRY_RUN_READY", "screenshot": screenshot_path, "fields": fields_filled}
        else:
            submit_btn = await best_form.query_selector("button[type='submit'], input[type='submit'], button:has-text('Submit'), button:has-text('Send'), input[value*='Send' i]")
            if not submit_btn:
                log_submission_result(clinic_name, domain, target_url, "NO_SUBMIT_BTN", "LIVE", "Form filled but no submit button found", screenshot_path)
                await page.close()
                return {"status": "NO_SUBMIT_BTN"}

            print("    [*] Live mode: Clicking submit button...")
            await submit_btn.click()
            await asyncio.sleep(4)

            confirm_screenshot = os.path.join(SCREENSHOTS_DIR, f"submitted_{domain}_{timestamp_int}.png")
            await page.screenshot(path=confirm_screenshot)
            log_submission_result(clinic_name, domain, target_url, "SUCCESS", "LIVE", f"Form submitted successfully. Fields: {','.join(fields_filled)}", confirm_screenshot)
            print("    [✓] Form submitted live successfully!")
            await page.close()
            return {"status": "SUCCESS", "screenshot": confirm_screenshot}

    except Exception as e:
        error_msg = str(e)
        print(f"    [x] Error during form processing: {error_msg}")
        log_submission_result(clinic_name, domain, target_url, "ERROR", "DRY_RUN" if dry_run else "LIVE", error_msg)
        if not page.is_closed():
            await page.close()
        return {"status": "ERROR", "error": error_msg}

async def run_pipeline(limit: int = 3, dry_run: bool = True, target_url: Optional[str] = None, clinic_name: Optional[str] = None):
    contacted_domains = load_contacted_domains()
    print(f"Loaded {len(contacted_domains)} previously contacted/skipped domains from registry.")
    
    targets = []
    if target_url:
        targets.append({
            "Company Name": clinic_name or "Aesthetic Clinic",
            "City": "Denver",
            "Website": target_url
        })
    else:
        candidate_files = [
            "/home/idrees/northstars/leads/verified_outreach_ready.csv",
            "/home/idrees/northstars/leads/raw_databases/Master_Qualified_Leads.csv"
        ]
        for fpath in candidate_files:
            if not os.path.exists(fpath):
                continue
            with open(fpath, mode="r", encoding="utf-8-sig") as f:
                reader = csv.DictReader(f)
                for row in reader:
                    site = row.get("Website", "").strip()
                    name = row.get("Company Name", "").strip()
                    city = row.get("City", "Dallas").strip()
                    dom = normalize_domain(site)
                    if site.startswith("http") and dom not in contacted_domains:
                        targets.append({"Company Name": name, "City": city, "Website": site})
                        contacted_domains.add(dom)
                        if len(targets) >= limit:
                            break
            if len(targets) >= limit:
                break

    print(f"Selected {len(targets)} unharvested targets for execution (Mode: {'DRY RUN' if dry_run else 'LIVE'}).")

    async with async_playwright() as p:
        browser = await p.chromium.launch(
            headless=True,
            args=[
                "--disable-blink-features=AutomationControlled",
                "--no-sandbox",
                "--disable-setuid-sandbox"
            ]
        )
        context = await browser.new_context(
            user_agent=random.choice(USER_AGENTS),
            locale="en-US",
            timezone_id="America/Chicago"
        )
        
        await context.add_init_script("""
            Object.defineProperty(navigator, 'webdriver', {
                get: () => undefined
            });
        """)

        for idx, t in enumerate(targets):
            res = await process_clinic_form(
                context=context,
                clinic_name=t["Company Name"],
                city=t["City"],
                website_url=t["Website"],
                dry_run=dry_run
            )
            if idx < len(targets) - 1:
                delay = random.uniform(5.0, 10.0) if dry_run else random.uniform(90.0, 180.0)
                print(f"[*] Sleeping {delay:.1f}s to maintain human cadence...")
                await asyncio.sleep(delay)

        await browser.close()

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Autonomous Clinic Contact Form Submitter")
    parser.add_argument("--limit", type=int, default=3, help="Number of clinics to process")
    parser.add_argument("--url", type=str, default=None, help="Target a specific website URL")
    parser.add_argument("--name", type=str, default=None, help="Clinic name when targeting specific URL")
    parser.add_argument("--live", action="store_true", help="Execute live submission (default is dry-run)")
    args = parser.parse_args()

    asyncio.run(run_pipeline(
        limit=args.limit,
        dry_run=not args.live,
        target_url=args.url,
        clinic_name=args.name
    ))
