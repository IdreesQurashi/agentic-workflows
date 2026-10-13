# Core Engineering and Infrastructure Operational Instructions

These standard operating procedures define the step by step workflow for engineering n8n production automations, managing local server backends, authoring minimal reproducer scripts, and hardening infrastructure. Every procedure addresses real world failures documented across historical infrastructure sessions.

***

## 1. n8n Workflow JSON Export and Canvas Paste Schema

### Problem
Generating incomplete node arrays `[{...}]` caused n8n import dialogs to crash and reject pasted workflows.

### Idrees's Solution
"n8n rejected the paste because n8n requires a top level wrapper object with "nodes": [...] and "connections": [...] now send again the testing for 2nd path"

### Enki's Proposed Solution
Every n8n workflow exported or generated for manual canvas import must adhere to the complete canonical JSON wrapper:
```json
{
  "name": "Production Workflow Name",
  "nodes": [
    { ... }
  ],
  "connections": {
    "Node Name": {
      "main": [
        [
          { "node": "Next Node Name", "type": "main", "index": 0 }
        ]
      ]
    }
  },
  "settings": { "executionOrder": "v1" }
}
```
Validate that every node mentioned in connections exists in the nodes array before delivering the JSON snippet.

***

## 2. Programmatic Webhook Verification Protocol

### Problem
Instructing the user to click a webhook link in the browser triggered an HTTP GET request on an HTTP POST endpoint, resulting in HTTP 405 Method Not Allowed.

### Idrees's Solution
"fuck you" (accompanied by screenshot of `{"detail":"Method Not Allowed"}`)

### Enki's Proposed Solution
Whenever a webhook endpoint is deployed, supply a ready to execute cURL command directly in chat:
```bash
curl -X POST http://localhost:8000/webhook/ingest \
  -H "Content-Type: application/json" \
  -d '{"event": "test_submission", "status": "verified"}'
```
Provide the exact expected response body so the user or test runner can verify successful ingestion in a single move.

***

## 3. Minimal Error Reproduction Protocol (Self Annealing)

### Problem
Modifying complex scripts directly in `execution/` based on intuition often introduced secondary regressions and syntax errors.

### Idrees's Solution
"Self Annealing Protocol: When a script or tool breaks, fix the script, verify the fix, and document the permanent solution in the relevant directive under directives/."

### Enki's Proposed Solution
Execute the 4 step reproduction cycle:
1. Capture the exact stack trace and failing inputs.
2. Author a minimal standalone reproduction script at `.tmp/reproduce_error.py`.
3. Run `/home/idrees/job_agent/.venv/bin/python3 .tmp/reproduce_error.py` and confirm the crash reproduces faithfully.
4. Apply the code fix, confirm the reproducer exits with code 0, and delete the temporary reproducer.

***

## 4. Production n8n Backup and Upgrade Procedure

### Problem
Running n8n version upgrades without local backups risked database schema corruption and credential loss across active workflows.

### Idrees's Solution
"Deliver: (1) automated pre update backup workflow, exports all workflow JSONs + credentials list"

### Enki's Proposed Solution
Execute the pre update runbook before upgrading the local n8n instance:
1. Export all active workflow JSONs via the n8n REST API to `/home/idrees/Documents/n8n_backups/YYYY-MM-DD/`.
2. Back up the SQLite database file located at `~/.n8n/database.sqlite`.
3. Pull the updated container or package.
4. Trigger the health monitor test workflow to verify webhook reception, execution logs, and database connectivity.

***

## 5. Dedicated Headless Playwright Execution

### Problem
Automation scripts attempting to bind to local graphical browsers crashed user sessions and failed when graphical display servers were unavailable.

### Idrees's Solution
"Dedicated Backend Playwright: Web automation and scraping must run inside the dedicated backend virtual environment (/home/idrees/job_agent/.venv/bin/python3)."

### Enki's Proposed Solution
All Playwright scripts must configure isolated headless execution:
```python
browser = await p.chromium.launch(
    headless=True,
    args=["--no-sandbox", "--disable-dev-shm-usage", "--disable-gpu"]
)
context = await browser.new_context(
    viewport={"width": 1280, "height": 800},
    user_agent="Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36"
)
```
Ensure browser contexts and pages are explicitly closed in `finally` blocks to prevent dangling memory leaks.
