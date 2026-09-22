import sys
from pathlib import Path
EXECUTION_DIR = Path(__file__).resolve().parent.parent
if str(EXECUTION_DIR) not in sys.path:
    sys.path.insert(0, str(EXECUTION_DIR))
from _root import DATA_LEADS_DIR, LEADS_100K, LEADS_100_IG, LEADS_QUALIFIED, LEADS_FILTERED, URLS_FILE, LEADS_DB, ENV_FILE
from dotenv import load_dotenv
load_dotenv(ENV_FILE)
import csv

input_file = LEADS_100_IG
output_file = LEADS_100K

with open(input_file, 'r', encoding='utf-8') as f:
    reader = csv.DictReader(f)
    rows = list(reader)

filtered_rows = []
for row in rows:
    try:
        followers = int(row['Followers'])
    except:
        followers = 0
        
    if followers <= 100000:
        filtered_rows.append(row)

with open(output_file, 'w', newline='', encoding='utf-8') as f:
    if len(filtered_rows) > 0:
        writer = csv.DictWriter(f, fieldnames=filtered_rows[0].keys())
        writer.writeheader()
        writer.writerows(filtered_rows)

print(f"Original Count: {len(rows)}")
print(f"After <100K Filter: {len(filtered_rows)}")
