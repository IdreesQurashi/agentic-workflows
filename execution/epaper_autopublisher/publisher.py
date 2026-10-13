import os
import sys
import json
import argparse
from datetime import datetime
from wp_client import WordPressClient
from gmail_reader import GmailReader

CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
CONFIG_PATH = os.path.join(CURRENT_DIR, "config.json")

def load_config() -> dict:
    if not os.path.exists(CONFIG_PATH):
        raise FileNotFoundError(f"Configuration file not found at {CONFIG_PATH}. Copy config.example.json to config.json.")
    with open(CONFIG_PATH, "r", encoding="utf-8") as f:
        return json.load(f)

def test_wp_connections(config: dict):
    print("=== Testing WordPress REST API Connections ===")
    for pub_key, pub_info in config.get("publications", {}).items():
        name = pub_info.get("name", pub_key)
        url = pub_info.get("wp_url", "")
        key = pub_info.get("api_key", "")
        
        if not key or "YOUR_" in key:
            print(f"[-] {name}: SKIPPED (API key not configured yet)")
            continue
            
        client = WordPressClient(url, key)
        res = client.check_connection()
        if res.get("success"):
            print(f"[+] {name}: SUCCESS (Connected as '{res.get('user')}', User ID: {res.get('id')})")
        else:
            print(f"[-] {name}: FAILED (Status: {res.get('status')}, Error: {res.get('error')})")

def process_publication(pub_key: str, pages: list, pub_cfg: dict, dry_run: bool = False, custom_date: str = None) -> dict:
    name = pub_cfg.get("name", pub_key)
    wp_url = pub_cfg.get("wp_url")
    api_key = pub_cfg.get("api_key")
    cat_id = pub_cfg.get("category_id", 42)
    author_id = pub_cfg.get("author_id", 1)
    
    print(f"\n--- Processing {name} ({len(pages)} pages) ---")
    if not pages:
        print(f"[*] No pages found for {name}. Skipping post creation.")
        return {"success": True, "created": False, "reason": "No pages"}
        
    if not api_key or "YOUR_" in api_key:
        print(f"[-] Cannot publish to {name}: API key missing in config.json")
        return {"success": False, "error": "API key missing"}

    client = WordPressClient(wp_url, api_key)
    
    # Generate post title formatted as DD-MM-YYYY (or use custom date)
    today_title = custom_date if custom_date else datetime.now().strftime("%d-%m-%Y")
    
    if dry_run:
        print(f"[*] DRY RUN: Would upload {len(pages)} pages and create post '{today_title}' in Category {cat_id}")
        for idx, p in enumerate(pages, start=1):
            print(f"    Page {idx}: {p['filename']} ({len(p.get('data', b''))} bytes)")
        return {"success": True, "dry_run": True, "pages": len(pages)}

    uploaded_pages = []
    for idx, p in enumerate(pages, start=1):
        fn = p.get("filename")
        data = p.get("data")
        mime = p.get("mime_type", "image/jpeg")
        
        print(f"[*] Uploading page {idx}/{len(pages)}: {fn}...")
        res = client.upload_media(fn, data, mime)
        if not res.get("success"):
            print(f"[-] Failed to upload {fn}: {res.get('error')}")
            return {"success": False, "error": f"Failed uploading {fn}: {res.get('error')}"}
            
        print(f"    Uploaded successfully -> Media ID {res.get('id')}")
        uploaded_pages.append(res)

    print(f"[*] Creating single unified DearFlip post '{today_title}'...")
    post_res = client.create_dearflip_post(today_title, uploaded_pages, category_id=cat_id, author_id=author_id)
    
    if post_res.get("success"):
        print(f"[+] Post published successfully!")
        print(f"    Post ID: {post_res.get('post_id')}")
        print(f"    Post URL: {post_res.get('link')}")
        print(f"    Total Pages Inside: {post_res.get('pages_count')}")
        return post_res
    else:
        print(f"[-] Failed to create post: {post_res.get('error')}")
        return post_res

def run_pipeline(dummy: bool = False, dry_run: bool = False, custom_date: str = None):
    config = load_config()
    pub_configs = config.get("publications", {})
    
    if dummy:
        print("=== Running Pipeline with Dummy Multi-Batch Data ===")
        email_bundles = GmailReader.generate_dummy_bundles()
        print(f"[+] Generated {len(email_bundles)} simulated email batches.")
    else:
        print("=== Running Pipeline with Live Gmail Ingestion ===")
        gcfg = config.get("gmail", {})
        if not gcfg.get("app_password") or "YOUR_" in gcfg.get("app_password"):
            print("[-] Gmail app password missing in config.json. Use --test-dummy to test without live Gmail.")
            sys.exit(1)
            
        reader = GmailReader(
            imap_server=gcfg.get("imap_server", "imap.gmail.com"),
            imap_port=gcfg.get("imap_port", 993),
            email_addr=gcfg.get("email"),
            app_password=gcfg.get("app_password"),
            sender_filter=gcfg.get("sender_filter")
        )
        print(f"[*] Connecting to {gcfg.get('imap_server')} as {gcfg.get('email')}...")
        email_bundles = reader.fetch_recent_newspaper_emails()
        print(f"[+] Found {len(email_bundles)} matching newspaper emails.")

    # Multi-batch aggregation across all received emails
    aggregated = GmailReader.partition_and_aggregate(email_bundles, pub_configs)
    
    print("\n=== Aggregation Summary ===")
    for pub_key, pages in aggregated.items():
        name = pub_configs.get(pub_key, {}).get("name", pub_key)
        filenames = [p["filename"] for p in pages]
        print(f"  {name}: {len(pages)} pages gathered -> {filenames}")

    # Process publications
    for pub_key, pages in aggregated.items():
        cfg = pub_configs.get(pub_key, {})
        process_publication(pub_key, pages, cfg, dry_run=dry_run, custom_date=custom_date)

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Antigravity E-Paper Auto Publisher")
    parser.add_argument("--test-wp", action="store_true", help="Test WordPress REST API connections")
    parser.add_argument("--test-dummy", action="store_true", help="Run with simulated multi-batch dummy data")
    parser.add_argument("--dry-run", action="store_true", help="Parse and aggregate without writing to WordPress")
    parser.add_argument("--live", action="store_true", help="Execute full live run from Gmail to WordPress")
    parser.add_argument("--date", type=str, default=None, help="Custom post date/title e.g. 03-10-2026")
    
    args = parser.parse_args()
    
    if args.test_wp:
        test_wp_connections(load_config())
    elif args.test_dummy:
        run_pipeline(dummy=True, dry_run=args.dry_run, custom_date=args.date)
    elif args.live:
        run_pipeline(dummy=False, dry_run=False, custom_date=args.date)
    elif args.dry_run:
        run_pipeline(dummy=False, dry_run=True, custom_date=args.date)
    else:
        parser.print_help()
