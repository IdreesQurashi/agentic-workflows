"""
Patch and update n8n workflow nodes with clean escaped node referencing syntax.
"""

import os, requests, json
from dotenv import load_dotenv

load_dotenv()
url = os.getenv('N8N_URL', 'http://localhost:5678')
key = os.getenv('N8N_API_KEY')
headers = {'X-N8N-API-KEY': key}

wf = requests.get(f'{url}/api/v1/workflows/rIqCVHyxpsogS2mW', headers=headers).json()

for n in wf['nodes']:
    if n['name'] == 'Filter Method 1: Production Triggers Only':
        n['position'] = [280, 140]
        n['parameters']['jsCode'] = """// METHOD 1: Exclude manual developer canvas runs (mode !== 'manual')
// Only monitor real scheduled triggers, webhooks, and sub-workflow executions
const rawExecutions = $('Fetch 24h Executions').first().json.data || [];
const prodExecutions = rawExecutions.filter(e => e.mode !== 'manual');

return [{
  json: {
    filterApplied: "Method 1: Production Triggers Only (mode != manual)",
    totalRawCount: rawExecutions.length,
    productionCount: prodExecutions.length,
    manualTestingCount: rawExecutions.length - prodExecutions.length,
    filteredExecutions: prodExecutions
  }
}];"""
    elif n['name'] == 'Filter Method 2: Active Workflows Only':
        n['position'] = [280, 460]
        n['parameters']['jsCode'] = """// METHOD 2: Scope strictly to workflows that are ACTIVE in production
// Draft / scratchpad workflows (active: false) are filtered out
const workflowsData = $('Fetch Workflows').first().json.data || [];
const rawExecutions = $('Fetch 24h Executions').first().json.data || [];

const activeWorkflowIds = new Set(workflowsData.filter(w => w.active === true).map(w => w.id));
const activeWorkflowExecutions = rawExecutions.filter(e => activeWorkflowIds.has(e.workflowId));

return [{
  json: {
    filterApplied: "Method 2: Active Workflows Only (active == true)",
    totalWorkflows: workflowsData.length,
    activeWorkflowsCount: activeWorkflowIds.size,
    totalRawExecutions: rawExecutions.length,
    activeWorkflowExecutionsCount: activeWorkflowExecutions.length,
    filteredExecutions: activeWorkflowExecutions
  }
}];"""

payload = {
    'name': wf['name'],
    'nodes': wf['nodes'],
    'connections': wf['connections'],
    'settings': wf.get('settings', {})
}

res = requests.put(f'{url}/api/v1/workflows/rIqCVHyxpsogS2mW', headers=headers, json=payload)
print('PUT status updating Method 1 & 2 code:', res.status_code)

# Export clean JSON
clean_wf = {
    'name': payload['name'],
    'nodes': payload['nodes'],
    'connections': payload['connections'],
    'settings': payload['settings']
}
with open('execution/workflows/n8n_health_monitor_workflow.json', 'w') as f:
    json.dump(clean_wf, f, indent=2)

print('Updated execution/workflows/n8n_health_monitor_workflow.json!')
