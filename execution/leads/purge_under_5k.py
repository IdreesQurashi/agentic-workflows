import sys
from pathlib import Path
EXECUTION_DIR = Path(__file__).resolve().parent.parent
if str(EXECUTION_DIR) not in sys.path:
    sys.path.insert(0, str(EXECUTION_DIR))
from _root import DATA_LEADS_DIR, LEADS_100K, LEADS_100_IG, LEADS_QUALIFIED, LEADS_FILTERED, URLS_FILE, LEADS_DB, ENV_FILE
from dotenv import load_dotenv
load_dotenv(ENV_FILE)
import csv
import os

directory = '/home/idrees/northstars/leads/daily leads database/'
files = ['Daily_Qualified_Leads_Sept16.csv', 'Daily_Qualified_Leads_Sept16_Batch2.csv']

total_before = 0
total_after = 0

for file_name in files:
    file_path = os.path.join(directory, file_name)
    if not os.path.exists(file_path):
        continue
        
    with open(file_path, 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        rows = list(reader)
        
    if not rows:
        continue
        
    total_before += len(rows)
    
    filtered_rows = []
    for row in rows:
        try:
            followers = int(row['Followers'])
        except:
            followers = 0
            
        if followers >= 5000 and followers <= 100000:
            filtered_rows.append(row)
            
    total_after += len(filtered_rows)
    
    with open(file_path, 'w', newline='', encoding='utf-8') as f:
        writer = csv.DictWriter(f, fieldnames=rows[0].keys())
        writer.writeheader()
        writer.writerows(filtered_rows)

print(f"Purge Complete.")
print(f"Original Count: {total_before}")
print(f"Surviving Leads (>5K Followers): {total_after}")
