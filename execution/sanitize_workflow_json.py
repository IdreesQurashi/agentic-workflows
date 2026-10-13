"""
Sanitize workflow JSON with proper escaped n8n node referencing syntax
for universal 10-minute deployment on any n8n instance.
"""

import json

with open('execution/workflows/n8n_health_monitor_workflow.json', 'r') as f:
    wf = json.load(f)

for n in wf['nodes']:
    if n['name'] in ['Fetch Workflows', 'Fetch 24h Executions']:
        headers = n['parameters'].get('headerParameters', {}).get('parameters', [])
        for h in headers:
            if h.get('name') == 'X-N8N-API-KEY':
                h['value'] = "={{ $('Set Config & 24h Window').first().json.n8nApiKey }}"
    elif n['name'] == 'Set Config & 24h Window':
        n['parameters']['jsCode'] = """const now = new Date();
const past24h = new Date(now.getTime() - (24 * 60 * 60 * 1000));

return [{
  json: {
    startedAfter: past24h.toISOString(),
    startedBefore: now.toISOString(),
    baseUrl: 'http://localhost:5678',
    externalBaseUrl: 'http://localhost:5678',
    n8nApiKey: 'PASTE_YOUR_N8N_API_KEY_HERE',
    recipientEmail: 'idreesqurashi.ai@gmail.com'
  }
}];"""

with open('execution/workflows/n8n_health_monitor_workflow.json', 'w') as f:
    json.dump(wf, f, indent=2)

print('Sanitized workflow JSON successfully.')
