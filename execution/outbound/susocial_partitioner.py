#!/usr/bin/env python3
"""SuSocial 4 Batch Partitioner and 13 Column Contact Formatter.

Formats leads into the strict 13 column SuSocial Contact tool schema and
divides them equally across 4 sterile CSV files for multi account distribution.
Enforces utf-8-sig encoding and Windows CRLF line endings.
"""

import os
import sys
import csv
import re
import argparse
from typing import List, Dict, Any

DEFAULT_INPUT_FILE = "/home/idrees/northstars/leads/raw_databases/Master_Qualified_Leads.csv"
OUTPUT_DIRS = [
    "/home/idrees/northstars/leads/new folder",
    "/home/idrees/northstars/leads/susocial_ready"
]

SUSOCIAL_13_HEADERS = [
    "Company Name",           # Col 1
    "First Name",             # Col 2 -> Mapped to NAME by SuSocial (Stores Username)
    "Phone",                  # Col 3
    "Address",                # Col 4 -> Mapped to GROUP NAME by SuSocial (Stores Company)
    "City",                   # Col 5
    "State",                  # Col 6 -> Mapped to MESSAGE by SuSocial (Stores Outreach Message)
    "Website",                # Col 7
    "Instagram Handle",       # Col 8 -> Used for deduplication by SuSocial
    "Instagram Profile URL",  # Col 9 -> Used for deduplication by SuSocial
    "Followers Count",        # Col 10
    "Anchor Procedure",       # Col 11
    "Outreach Message",       # Col 12
    "Tags"                    # Col 13
]

def clean_username(handle: str, profile_url: str) -> str:
    handle = (handle or "").strip()
    profile_url = (profile_url or "").strip()
    
    if handle:
        cleaned = handle.lstrip("@").strip()
        if "instagram.com/" in cleaned:
            match = re.search(r"instagram\.com/([^/?#]+)", cleaned)
            if match:
                return match.group(1).strip()
        cleaned = re.sub(r"[/?#].*$", "", cleaned).strip()
        if cleaned:
            return cleaned
            
    if profile_url:
        match = re.search(r"instagram\.com/([^/?#]+)", profile_url)
        if match:
            u = match.group(1).strip()
            if u:
                return u
                
    return ""

def generate_default_message(company_name: str, city: str) -> str:
    short_name = (company_name or "there").split()[0]
    clean_city = (city or "your area").split(",")[0]
    return f"Hey {short_name} team. Pulled a quick look at what a few {clean_city} practices are running in Meta ads right now, some pretty obvious gaps. Mind if I send over what I found?"

def load_and_standardize_leads(input_path: str) -> List[Dict[str, Any]]:
    if not os.path.exists(input_path):
        print(f"Error: Input file does not exist: {input_path}", file=sys.stderr)
        return []

    leads = []
    seen_usernames = set()
    seen_websites = set()

    with open(input_path, mode="r", encoding="utf-8-sig", errors="replace") as f:
        reader = csv.DictReader(f)
        for row in reader:
            company = row.get("Company Name") or row.get("company") or row.get("Title") or ""
            company = company.strip()
            
            handle = row.get("Instagram Handle") or row.get("instagram") or row.get("Handle") or ""
            profile_url = row.get("Instagram Profile URL") or row.get("profile_url") or ""
            
            username = clean_username(handle, profile_url)
            if not username:
                continue
                
            username_key = username.lower()
            if username_key in seen_usernames:
                continue
            seen_usernames.add(username_key)

            website = (row.get("Website") or row.get("website") or "").strip()
            if website:
                clean_web = re.sub(r"^https?://(www\.)?", "", website.lower()).rstrip("/")
                if clean_web in seen_websites:
                    continue
                seen_websites.add(clean_web)

            city = (row.get("City") or row.get("city") or "").strip()
            state = (row.get("State") or row.get("state") or "").strip()
            phone = (row.get("Phone") or row.get("phone") or "+1 555 555 5555").strip()
            address = (row.get("Address") or row.get("address") or city).strip()
            services = (row.get("Anchor Procedure") or row.get("services") or "Aesthetics & Medspa Services").strip()
            tags = (row.get("Tags") or "Northstars_B2B").strip()

            message = row.get("Outreach Message") or row.get("message") or ""
            if not message:
                message = generate_default_message(company, city)
            message = message.strip()

            leads.append({
                "company": company,
                "username": username,
                "phone": phone,
                "city": city,
                "state": state,
                "address": address,
                "website": website,
                "services": services,
                "message": message,
                "tags": tags
            })

    return leads

def write_partitioned_batches(leads: List[Dict[str, Any]], target_dirs: List[str], num_batches: int = 4):
    if not leads:
        print("No qualified leads available to partition.")
        return

    total = len(leads)
    batch_size = (total + num_batches - 1) // num_batches
    print(f"Total leads: {total}. Partitioning into {num_batches} batches (~{batch_size} leads each)...")

    for dir_path in target_dirs:
        os.makedirs(dir_path, exist_ok=True)
        for i in range(num_batches):
            batch_leads = leads[i * batch_size : (i + 1) * batch_size]
            filename = f"leads_part_{i + 1}.csv"
            out_file = os.path.join(dir_path, filename)

            with open(out_file, mode="w", encoding="utf-8-sig", newline="") as f:
                writer = csv.writer(f, quoting=csv.QUOTE_MINIMAL, lineterminator="\r\n")
                writer.writerow(SUSOCIAL_13_HEADERS)

                for r in batch_leads:
                    row_data = [""] * 13
                    row_data[0] = r["company"]
                    row_data[1] = r["username"]                         # UI NAME
                    row_data[2] = r["phone"]
                    row_data[3] = r["company"]                          # UI GROUP NAME
                    row_data[4] = r["city"]
                    row_data[5] = r["message"]                          # UI MESSAGE
                    row_data[6] = r["website"]
                    row_data[7] = r["username"]                         # Deduplication
                    row_data[8] = f"https://instagram.com/{r['username']}" # Profile URL
                    row_data[9] = "5000"                                # Followers Count
                    row_data[10] = r["services"]                        # Anchor Procedure
                    row_data[11] = r["message"]                         # Outreach Message
                    row_data[12] = r["tags"]                            # Tags
                    writer.writerow(row_data)

            print(f"  [SAVED] {out_file} -> {len(batch_leads)} leads")

def main():
    parser = argparse.ArgumentParser(description="Partition leads for SuSocial 4 account deployment")
    parser.add_argument("--input", default=DEFAULT_INPUT_FILE, help="Path to input leads CSV")
    parser.add_argument("--out-dir", action="append", help="Target output directory (can specify multiple)")
    parser.add_argument("--batches", type=int, default=4, help="Number of account batches (default 4)")
    args = parser.parse_args()

    target_dirs = args.out_dir if args.out_dir else OUTPUT_DIRS
    leads = load_and_standardize_leads(args.input)
    write_partitioned_batches(leads, target_dirs, num_batches=args.batches)

if __name__ == "__main__":
    main()
