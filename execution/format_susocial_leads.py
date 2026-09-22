import os
import csv
import re

LEADS_DIR = "/home/idrees/northstars/leads/new folder"

FU1_TEMPLATE = "Hey, this probably got buried, IG DMs are chaos. Still happy to send over what I found on the {procedure} ads running in {city} if you want it, quick read."
FU2_TEMPLATE = "All good if it's not the right time, I'll stop bugging you. Door's open whenever, just send a message if you ever want {city} customer's breakdown."

def clean_username(handle, profile_url):
    handle = (handle or "").strip()
    profile_url = (profile_url or "").strip()
    
    # Try handle first
    if handle:
        cleaned = handle.lstrip("@").strip()
        if "instagram.com/" in cleaned:
            match = re.search(r"instagram\.com/([^/?#]+)", cleaned)
            if match:
                return match.group(1).strip()
        cleaned = re.sub(r"[/?#].*$", "", cleaned).strip()
        if cleaned:
            return cleaned
            
    # Try profile url
    if profile_url:
        match = re.search(r"instagram\.com/([^/?#]+)", profile_url)
        if match:
            u = match.group(1).strip()
            if u:
                return u
                
    return ""

def process_file(file_name, batch_name):
    input_path = os.path.join(LEADS_DIR, file_name)
    if not os.path.exists(input_path):
        print(f"Error: {input_path} does not exist.")
        return []

    rows = []
    with open(input_path, mode="r", encoding="utf-8-sig", errors="replace") as f:
        reader = csv.DictReader(f)
        for idx, row in enumerate(reader, start=1):
            company = row.get("Company Name", "").strip()
            first_name = row.get("First Name", "").strip()
            city = row.get("City", "").strip()
            handle = row.get("Instagram Handle", "").strip()
            profile_url = row.get("Instagram Profile URL", "").strip()
            procedure = row.get("Anchor Procedure", "").strip()
            message = row.get("Outreach Message", "").strip()
            
            # Clean username
            username = clean_username(handle, profile_url)
            
            # Fallback for procedure if missing
            if not procedure and message:
                proc_match = re.search(r"for (.*?) right now", message)
                if proc_match:
                    procedure = proc_match.group(1).strip()
                    
            # Fallback for city if missing
            if not city and message:
                city_match = re.search(r"what a few (.*?) (?:medspa|Medical spa|Plastic surgeon|Facial spa|Skin care|hair restoration|Cosmetic)", message, re.IGNORECASE)
                if city_match:
                    city = city_match.group(1).strip()
            
            if not city:
                city = "the area"
                
            # Build follow ups
            fu1 = FU1_TEMPLATE.format(procedure=procedure, city=city)
            fu2 = FU2_TEMPLATE.format(city=city)
            
            # Remove any unintended double spaces
            fu1 = re.sub(r"  +", " ", fu1).strip()
            fu2 = re.sub(r"  +", " ", fu2).strip()
            
            rows.append({
                "Username": username,
                "Message": message,
                "Followup_1": fu1,
                "Followup_2": fu2,
                "Company_Name": company,
                "City": city,
                "Anchor_Procedure": procedure,
                "Original_Handle": handle,
                "Batch": batch_name,
                "Row_Index": idx
            })
            
    return rows

def main():
    parts = [
        ("leads_part_1.csv", "Part_1"),
        ("leads_part_2.csv", "Part_2"),
        ("leads_part_3.csv", "Part_3"),
        ("leads_part_4.csv", "Part_4")
    ]
    
    all_leads = []
    
    for filename, batch in parts:
        leads = process_file(filename, batch)
        all_leads.extend(leads)
        print(f"Processed {len(leads)} leads from {filename}")
        
        part_num = batch.split("_")[1]
        out_part_path = os.path.join(LEADS_DIR, f"leads_part_{part_num}_susocial.csv")
        with open(out_part_path, "w", encoding="utf-8", newline="") as out_f:
            writer = csv.writer(out_f, quoting=csv.QUOTE_ALL)
            writer.writerow(["Username", "Message", "Followup_1", "Followup_2"])
            for item in leads:
                writer.writerow([item["Username"], item["Message"], item["Followup_1"], item["Followup_2"]])
        print(f"Saved {out_part_path}")
        
        # SuSocial ready 2-column files:
        out_init_path = os.path.join(LEADS_DIR, f"leads_part_{part_num}_initial.csv")
        with open(out_init_path, "w", encoding="utf-8", newline="") as out_f:
            writer = csv.writer(out_f, quoting=csv.QUOTE_ALL)
            writer.writerow(["Username", "Message"])
            for item in leads:
                writer.writerow([item["Username"], item["Message"]])
                
        out_fu1_path = os.path.join(LEADS_DIR, f"leads_part_{part_num}_fu1.csv")
        with open(out_fu1_path, "w", encoding="utf-8", newline="") as out_f:
            writer = csv.writer(out_f, quoting=csv.QUOTE_ALL)
            writer.writerow(["Username", "Message"])
            for item in leads:
                writer.writerow([item["Username"], item["Followup_1"]])
                
        out_fu2_path = os.path.join(LEADS_DIR, f"leads_part_{part_num}_fu2.csv")
        with open(out_fu2_path, "w", encoding="utf-8", newline="") as out_f:
            writer = csv.writer(out_f, quoting=csv.QUOTE_ALL)
            writer.writerow(["Username", "Message"])
            for item in leads:
                writer.writerow([item["Username"], item["Followup_2"]])

    # Master Unified 4-column
    master_lean_path = os.path.join(LEADS_DIR, "all_leads_susocial_clean.csv")
    with open(master_lean_path, "w", encoding="utf-8", newline="") as out_f:
        writer = csv.writer(out_f, quoting=csv.QUOTE_ALL)
        writer.writerow(["Username", "Message", "Followup_1", "Followup_2"])
        for item in all_leads:
            writer.writerow([item["Username"], item["Message"], item["Followup_1"], item["Followup_2"]])
    print(f"Saved {master_lean_path} ({len(all_leads)} leads)")

    # Master Full
    master_full_path = os.path.join(LEADS_DIR, "all_leads_susocial_master.csv")
    with open(master_full_path, "w", encoding="utf-8", newline="") as out_f:
        writer = csv.writer(out_f, quoting=csv.QUOTE_ALL)
        writer.writerow(["Username", "Message", "Followup_1", "Followup_2", "Anchor_Procedure", "City", "Company_Name", "Batch"])
        for item in all_leads:
            writer.writerow([
                item["Username"],
                item["Message"],
                item["Followup_1"],
                item["Followup_2"],
                item["Anchor_Procedure"],
                item["City"],
                item["Company_Name"],
                item["Batch"]
            ])
    print(f"Saved {master_full_path}")

    # Master 2-column ready for direct SuSocial import
    for stage, col_name, suffix in [("initial", "Message", "all_leads_initial.csv"),
                                    ("followup 1", "Followup_1", "all_leads_fu1.csv"),
                                    ("followup 2", "Followup_2", "all_leads_fu2.csv")]:
        stage_path = os.path.join(LEADS_DIR, suffix)
        with open(stage_path, "w", encoding="utf-8", newline="") as out_f:
            writer = csv.writer(out_f, quoting=csv.QUOTE_ALL)
            writer.writerow(["Username", "Message"])
            for item in all_leads:
                writer.writerow([item["Username"], item[col_name]])
        print(f"Saved {stage_path}")

    empty_usernames = [item for item in all_leads if not item["Username"]]
    if empty_usernames:
        print(f"WARNING: {len(empty_usernames)} leads had empty usernames:")
        for item in empty_usernames:
            print(f"  Batch: {item['Batch']}, Row: {item['Row_Index']}, Company: {item['Company_Name']}, Handle: {item['Original_Handle']}")
    else:
        print("SUCCESS: 100% of leads have valid usernames!")

if __name__ == "__main__":
    main()
