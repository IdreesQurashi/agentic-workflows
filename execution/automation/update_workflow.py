import sys
from pathlib import Path
EXECUTION_DIR = Path(__file__).resolve().parent.parent
if str(EXECUTION_DIR) not in sys.path:
    sys.path.insert(0, str(EXECUTION_DIR))
from _root import DATA_WORKFLOWS_DIR
import json
import requests
import os

with open(DATA_WORKFLOWS_DIR / 'workflow.json', 'r') as f:
    wf = json.load(f)

for node in wf['nodes']:
    if node['type'] == 'n8n-nodes-base.code' and node['name'] == 'Top 5 posts filter':
        node['parameters']['jsCode'] = "MODIFIED CODE 3"

payload = {
    "name": wf.get("name"),
    "nodes": wf.get("nodes"),
    "connections": wf.get("connections"),
    "settings": wf.get("settings")
}

url = "http://localhost:5678/api/v1/workflows/ozURtig5uprexCmE"
headers = {
    "X-N8N-API-KEY": os.environ.get('N8N_API_KEY', 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIyYjYyNjA5OC1jNDM4LTQ2N2UtOGJlYi1jNDRiY2YxMzZkYTMiLCJpc3MiOiJuOG4iLCJhdWQiOiJwdWJsaWMtYXBpIiwianRpIjoiNWU5ZjE3MTEtOTIzOS00MmQ1LTlkYWMtZTdlMmJlYzRiNjMyIiwiaWF0IjoxNzg5MTg1OTQwfQ.M2mQj6I457zgCdMf7cM8Ab_wxP2Lg0xkGm2TTyOoHv4')
}
resp = requests.put(url, headers=headers, json=payload)
with open(DATA_WORKFLOWS_DIR / 'put_resp.json', 'w') as f:
    f.write(resp.text)
print(resp.status_code)
