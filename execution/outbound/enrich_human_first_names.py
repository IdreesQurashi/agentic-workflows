#!/usr/bin/env python3
"""Enrich Qualified Leads with Human-Selected First Names and Natural Outreach Copy.

Selects personal first names for individual practitioners, doctors, and founders.
For multi-provider clinics, generates natural clean team salutations (e.g. 'Adore team').
Eliminates robotic placeholders ('Owner') and broken automated fragments.
"""

import os
import sys
import csv
import re
import argparse
from typing import Dict, Any, Tuple

# Common English first names & doctor titles regex
DOCTOR_HANDLE_REGEX = re.compile(r"^(?:@)?(?:dr|doctor)[._]?([a-zA-Z]{3,15})", re.IGNORECASE)
NURSE_HANDLE_REGEX = re.compile(r"^(?:@)?(?:nurse|injector|rn|np|pa)[._]?([a-zA-Z]{3,15})", re.IGNORECASE)

# Words that should NEVER be treated as a human personal name
BUSINESS_WORDS_BLACKLIST = {
    "medspa", "medical", "spa", "aesthetics", "aesthetic", "aesthetix", "clinic", "center", "skin",
    "laser", "lounge", "bar", "care", "health", "wellness", "beauty", "cosmetic", "cosmetics",
    "rejuvenation", "face", "body", "boutique", "studio", "foundrie", "group", "injectables",
    "haus", "lab", "room", "collective", "institute", "couture", "district", "artistry",
    "haven", "alchemy", "glow", "pure", "radiance", "elite", "prime", "restore", "solutions",
    "restor", "vive", "elan", "cherry", "blue", "point", "karas", "charm", "the", "rx",
    "denver", "seattle", "atlanta", "phoenix", "las", "vegas", "tampa", "cleveland", "experts",
    "pittsburgh", "dallas", "austin", "houston", "miami", "chicago", "boston", "design",
    "definition", "nature", "touch", "choice", "concept", "precision", "glamour", "bliss"
}

def clean_company_name_for_team(raw_name: str, city: str = "") -> str:
    """Clean company name to produce natural team salutation: e.g. 'Adore team', 'Luxe Room team'."""
    name = raw_name.strip()
    
    # Remove city if appended like ' - Denver Cherry Creek' or ', Seattle'
    if city:
        name = re.sub(rf"\s*[-–—|,]\s*{re.escape(city)}.*$", "", name, flags=re.IGNORECASE)
    name = re.sub(r"\s*[-–—|]\s*(?:Denver|Seattle|Atlanta|Phoenix|Las Vegas|Tampa|Cleveland|Pittsburgh|Dallas|Austin|Houston|Miami|Chicago|Boston|Cherry Creek|Buckhead|Downtown|North|South|East|West).*$", "", name, flags=re.IGNORECASE)
    
    # Strip leading 'The '
    name = re.sub(r"^The\s+", "", name, flags=re.IGNORECASE)
    
    # Strip common business suffixes in order
    suffixes = [
        r"\s*&\s*Med\s*Spa.*$",
        r"\s*&\s*Medical\s*Spa.*$",
        r"\s*&\s*Aesthetics.*$",
        r"\s+Medical\s+Spa.*$",
        r"\s+Med\s+Spa.*$",
        r"\s+MedSpa.*$",
        r"\s+Medispa.*$",
        r"\s+Aesthetics\s+&\s+Wellness.*$",
        r"\s+Aesthetics\s+and\s+Wellness.*$",
        r"\s+Medical\s+Aesthetics.*$",
        r"\s+Cosmetic\s+Clinic.*$",
        r"\s+Plastic\s+Surgery.*$",
        r"\s+Dermatology.*$",
        r"\s+Skin\s+Clinic.*$",
        r"\s+Laser\s+Clinic.*$",
        r"\s+Laser\s+&\s+Med\s+Spa.*$",
        r"\s+Aesthetic\s+Center.*$",
        r"\s+Aesthetics.*$",
        r"\s+Aesthetix.*$",
        r"\s+Cosmetics.*$",
        r"\s+Spa.*$",
        r"\s+Clinic.*$",
        r"\s+Center.*$",
        r"\s+Studio.*$",
        r"\s+Lounge.*$",
        r"\s+LLC.*$",
        r"\s+Inc.*$"
    ]
    for suf in suffixes:
        name = re.sub(suf, "", name, flags=re.IGNORECASE).strip()
        
    # Strip trailing punctuation or conjunctions: '&', 'and', '-', ','
    name = re.sub(r"\s*(?:&|and|-|,|\+)\s*$", "", name, flags=re.IGNORECASE).strip()
    
    if not name or len(name) < 2:
        name = raw_name.split()[0] if raw_name else "Clinic"
        
    return f"{name} team"

def extract_human_first_name(company_name: str, handle: str, city: str = "") -> Tuple[str, str]:
    """Extract personal first name or clean team salutation.
    
    Returns:
        (first_name_str, type_str) where type_str is 'Personal' or 'Team'
    """
    clean_handle = handle.replace("@", "").strip()
    
    # 1. Check Handle for Doctor Name (e.g. @drstevengoldman -> Steven, @dr_jason_plasticsurgery -> Jason)
    m_doc = DOCTOR_HANDLE_REGEX.match(clean_handle)
    if m_doc:
        candidate = m_doc.group(1).capitalize()
        if candidate.lower() not in BUSINESS_WORDS_BLACKLIST and len(candidate) >= 3:
            return candidate, "Personal"

    # 2. Check Handle for Nurse / Injector Name (e.g. @nursekristen_rn -> Kristen)
    m_nurse = NURSE_HANDLE_REGEX.match(clean_handle)
    if m_nurse:
        candidate = m_nurse.group(1).capitalize()
        if candidate.lower() not in BUSINESS_WORDS_BLACKLIST and len(candidate) >= 3:
            return candidate, "Personal"

    # 3. Check Handle for Personal Name + Credentials (e.g. @jamesridgwaymd -> James, @stevengreenemd -> Steven)
    for cred in ["md", "rn", "np", "pa", "do", "dc"]:
        if clean_handle.lower().endswith(cred) and len(clean_handle) > len(cred) + 3:
            base = clean_handle[:-len(cred)].rstrip("._-")
            for name_cand in ["james", "steven", "steve", "david", "michael", "john", "sarah", "jessica", "amanda", "katie", "chloe", "alex", "rachel", "emily", "lauren", "ashley", "brittany", "morgan", "taylor", "jordan", "danielle"]:
                if base.lower().startswith(name_cand):
                    return name_cand.capitalize(), "Personal"

    # 4. Check Company Name for 'by [Name]' (e.g. 'Tru Beauty by Trevor' -> Trevor, 'Beauty by Sarah' -> Sarah)
    m_by = re.search(r"\bby\s+([A-Z][a-z]{2,15})\b", company_name, re.IGNORECASE)
    if m_by:
        candidate = m_by.group(1).capitalize()
        if candidate.lower() not in BUSINESS_WORDS_BLACKLIST:
            return candidate, "Personal"

    # 5. Check Company Name for 'Dr. [FirstName] [LastName]'
    m_dr_comp = re.search(r"\bDr\.?\s+([A-Z][a-z]{2,15})\b", company_name)
    if m_dr_comp:
        candidate = m_dr_comp.group(1).capitalize()
        if candidate.lower() not in BUSINESS_WORDS_BLACKLIST:
            return candidate, "Personal"

    # 6. Check Company Name for Known Founder Names (e.g. 'Sherisse Hill Aesthetic Derm' -> Sherisse)
    first_word = company_name.split()[0].replace(",", "").replace(".", "").strip()
    if first_word.lower() in ["sherisse", "trevor", "jessica", "sarah", "amanda", "chloe", "katie", "rachel", "emily", "lauren", "danielle", "steven", "james", "david", "michael", "christina", "elizabeth", "victoria", "hannah", "megan", "kristen"]:
        return first_word.capitalize(), "Personal"

    # 7. Fallback to Natural Clean Team Salutation (e.g. 'Adore team', 'Luxe Room team')
    team_name = clean_company_name_for_team(company_name, city)
    return team_name, "Team"

def build_outreach_message(first_name: str, city: str) -> str:
    """Generate high conversion, natural Western founder cold DM."""
    target_city = city.strip() if city else "metro"
    return f"Hey {first_name}. Pulled a quick look at what a few {target_city} practices are running in Meta ads right now, some pretty obvious gaps. Mind if I send over what I found?"

def clean_phone_number(raw_phone: str) -> str:
    """Clean phone number from schema JSON garbage if present."""
    if not raw_phone:
        return ""
    if "@context" in raw_phone or "{" in raw_phone:
        m = re.search(r"\(?\d{3}\)?[-.\s]?\d{3}[-.\s]?\d{4}", raw_phone)
        return m.group(0) if m else ""
    return raw_phone

def process_file(csv_path: str):
    """Enrich a single CSV file with human first names and updated outreach messages."""
    if not os.path.exists(csv_path):
        print(f"[SKIP] File not found: {csv_path}")
        return

    with open(csv_path, "r", encoding="utf-8-sig", errors="ignore") as f:
        rows = list(csv.DictReader(f))

    if not rows:
        print(f"[SKIP] Empty file: {csv_path}")
        return

    fieldnames = list(rows[0].keys())
    if "Name_Type" not in fieldnames:
        fieldnames.append("Name_Type")

    personal_count = 0
    team_count = 0

    for row in rows:
        biz_name = row.get("Company Name", "")
        handle = row.get("Instagram Handle", "")
        city = row.get("City", "")

        first_name, name_type = extract_human_first_name(biz_name, handle, city)
        row["First Name"] = first_name
        row["Name_Type"] = name_type
        row["Outreach Message"] = build_outreach_message(first_name, city)
        row["Phone"] = clean_phone_number(row.get("Phone", ""))

        if name_type == "Personal":
            personal_count += 1
        else:
            team_count += 1

    with open(csv_path, "w", newline="\r\n", encoding="utf-8-sig") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)

    print(f"Enriched {len(rows)} leads in {os.path.basename(csv_path)}:")
    print(f"  * Personal Names Isolated: {personal_count}")
    print(f"  * Clean Team Salutations:  {team_count}")

def main():
    parser = argparse.ArgumentParser(description="Enrich Qualified Leads with Human First Names")
    parser.add_argument("--file", help="Specific CSV file to enrich")
    parser.add_argument("--dir", default="/home/idrees/northstars/leads/susocial_ready_fresh_400", help="Directory of audited files")
    args = parser.parse_args()

    if args.file:
        process_file(args.file)
    else:
        for p in [1, 2, 3, 4]:
            fpath = os.path.join(args.dir, f"fresh_400_part_{p}_audited.csv")
            process_file(fpath)
        master_path = os.path.join(args.dir, "fresh_400_master_audited.csv")
        process_file(master_path)

if __name__ == "__main__":
    main()
