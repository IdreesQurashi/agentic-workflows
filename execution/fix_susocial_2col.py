import os
import csv
import re
import shutil

LEADS_DIR = "/home/idrees/northstars/leads/new folder"
BACKUP_DIR = "/home/idrees/Antigravity/Agentic Workflows-20260907T212811Z-1-001/Agentic Workflows/.tmp/backup_raw_leads"

def clean_username(handle, profile_url):
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

def process_raw_file(input_path, skip_first_n=0):
    rows = []
    with open(input_path, mode="r", encoding="utf-8-sig", errors="replace") as f:
        reader = csv.DictReader(f)
        for idx, row in enumerate(reader, start=1):
            if idx <= skip_first_n:
                continue
                
            handle = row.get("Instagram Handle", "").strip()
            profile_url = row.get("Instagram Profile URL", "").strip()
            message = row.get("Outreach Message", "").strip()
            
            username = clean_username(handle, profile_url)
            
            rows.append({
                "Username": username,
                "Message": message
            })
            
    return rows

def main():
    configs = [
        ("leads_part_1.csv", 20),
        ("leads_part_2.csv", 0),
        ("leads_part_3.csv", 0),
        ("leads_part_4.csv", 0)
    ]
    
    for filename, skip_n in configs:
        backup_src = os.path.join(BACKUP_DIR, filename)
        data = process_raw_file(backup_src, skip_first_n=skip_n)
        
        out_path = os.path.join(LEADS_DIR, filename)
        with open(out_path, "w", encoding="utf-8", newline="") as f:
            writer = csv.writer(f, quoting=csv.QUOTE_MINIMAL)
            writer.writerow(["Username", "Message"])
            for r in data:
                writer.writerow([r["Username"], r["Message"]])
        print(f"Wrote {filename}: {len(data)} leads (strictly Username,Message).")

    # Verify directory contents
    final_files = os.listdir(LEADS_DIR)
    print("\nFinal directory contents:")
    for f in sorted(final_files):
        print(f"  {f}")

if __name__ == "__main__":
    main()
