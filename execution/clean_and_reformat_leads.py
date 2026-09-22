import os
import csv
import re
import shutil

LEADS_DIR = "/home/idrees/northstars/leads/new folder"
BACKUP_DIR = "/home/idrees/Antigravity/Agentic Workflows-20260907T212811Z-1-001/Agentic Workflows/.tmp/backup_raw_leads"

FU1_TEMPLATE = "Hey, this probably got buried, IG DMs are chaos. Still happy to send over what I found on the {procedure} ads running in {city} if you want it, quick read."
FU2_TEMPLATE = "All good if it's not the right time, I'll stop bugging you. Door's open whenever, just send a message if you ever want that {city_breakdown} breakdown."

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
                
            company = row.get("Company Name", "").strip()
            city = row.get("City", "").strip()
            handle = row.get("Instagram Handle", "").strip()
            profile_url = row.get("Instagram Profile URL", "").strip()
            procedure = row.get("Anchor Procedure", "").strip()
            message = row.get("Outreach Message", "").strip()
            
            username = clean_username(handle, profile_url)
            
            if not procedure and message:
                proc_match = re.search(r"for (.*?) right now", message)
                if proc_match:
                    procedure = proc_match.group(1).strip()
                    
            if not city and message:
                city_match = re.search(r"what a few (.*?) (?:medspa|Medical spa|Plastic surgeon|Facial spa|Skin care|hair restoration|Cosmetic)", message, re.IGNORECASE)
                if city_match:
                    city = city_match.group(1).strip()
            
            if not city:
                city = "the area"
                
            # City breakdown phrasing for FU2
            if city.lower() == "the area":
                city_breakdown = "area"
            elif city.lower().startswith("the "):
                city_breakdown = city[4:].strip()
            else:
                city_breakdown = city
                
            fu1 = FU1_TEMPLATE.format(procedure=procedure, city=city)
            fu2 = FU2_TEMPLATE.format(city_breakdown=city_breakdown)
            
            fu1 = re.sub(r"  +", " ", fu1).strip()
            fu2 = re.sub(r"  +", " ", fu2).strip()
            
            rows.append({
                "Username": username,
                "Message": message,
                "Followup_1": fu1,
                "Followup_2": fu2
            })
            
    return rows

def main():
    os.makedirs(BACKUP_DIR, exist_ok=True)
    
    # 1. Backup the 4 raw files
    raw_files = ["leads_part_1.csv", "leads_part_2.csv", "leads_part_3.csv", "leads_part_4.csv"]
    for rf in raw_files:
        src = os.path.join(LEADS_DIR, rf)
        dst = os.path.join(BACKUP_DIR, rf)
        if os.path.exists(src) and not os.path.exists(dst):
            shutil.copy2(src, dst)
            print(f"Backed up {rf} to {dst}")

    # 2. Process each file
    configs = [
        ("leads_part_1.csv", 20),  # Skip first 20 leads
        ("leads_part_2.csv", 0),
        ("leads_part_3.csv", 0),
        ("leads_part_4.csv", 0)
    ]
    
    processed_data = {}
    for filename, skip_n in configs:
        backup_src = os.path.join(BACKUP_DIR, filename)
        # Process from the clean backup
        data = process_raw_file(backup_src, skip_first_n=skip_n)
        processed_data[filename] = data
        print(f"Processed {filename}: {len(data)} leads (skipped {skip_n})")

    # 3. Clean up the entire LEADS_DIR, leaving strictly the 4 target files
    for entry in os.listdir(LEADS_DIR):
        file_path = os.path.join(LEADS_DIR, entry)
        if os.path.isfile(file_path):
            os.remove(file_path)
            print(f"Removed extra file: {entry}")

    # 4. Write the 4 cleanly formatted CSV files
    for filename, rows in processed_data.items():
        out_path = os.path.join(LEADS_DIR, filename)
        with open(out_path, "w", encoding="utf-8", newline="") as f:
            writer = csv.writer(f, quoting=csv.QUOTE_ALL)
            writer.writerow(["Username", "Message", "Followup_1", "Followup_2"])
            for r in rows:
                writer.writerow([r["Username"], r["Message"], r["Followup_1"], r["Followup_2"]])
        print(f"Wrote clean {filename} with {len(rows)} leads.")

    # 5. Verify contents of directory
    final_files = os.listdir(LEADS_DIR)
    print("\nFinal directory contents:")
    for f in sorted(final_files):
        print(f"  {f}")
    assert len(final_files) == 4, f"Expected 4 files, got {len(final_files)}"
    print("\nSUCCESS: Exactly 4 files present in the folder!")

if __name__ == "__main__":
    main()
