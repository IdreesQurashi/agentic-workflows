# Core Engineering, n8n and Infrastructure High Priority Rules

These hard invariants govern all backend automation, n8n workflow engineering, API server deployments, and infrastructure management. Every rule addresses critical technical failures from historical sessions.

***

## 1. Prohibition of Testing POST Webhooks via Browser Navigation

### Problem
The model instructed the user to test a FastAPI webhook by clicking the URL in the browser address bar, which issued an HTTP GET request to an endpoint configured exclusively for HTTP POST, resulting in HTTP 405 Method Not Allowed.

### Idrees's Solution
"fuck you" (accompanied by screenshot of `{"detail":"Method Not Allowed"}`)

### Enki's Proposed Solution
Never test or instruct a user to test an HTTP POST webhook via browser address bar navigation. All webhook verification must be executed programmatically via cURL, Python requests, or Postman using explicit POST methods and valid JSON bodies.

***

## 2. Prohibition of Multi Input Overlap Without Merge Nodes

### Problem
The model connected two separate incoming workflow branches directly into a single downstream action node in n8n without an intermediate Merge node, causing unexpected race conditions and split executions.

### Idrees's Solution
"llm dont you think anything about these two inputs in same lane what is the purpose motherfucker and also why you dont try again for the 21"

### Enki's Proposed Solution
Strict adherence to n8n DAG execution patterns. Multiple incoming execution lines must pass through an explicit Merge node configured for append, combine, or wait modes before reaching shared downstream nodes.

***

## 3. Dedicated Virtual Environment Target Mandate

### Problem
Executing Python scripts via global `python3` caused 68 terminal crashes with `ModuleNotFoundError` because essential libraries (Playwright, bs4, pydantic, google genai) were installed exclusively inside isolated project environments.

### Idrees's Solution
"Dedicated Backend Playwright: Web automation and scraping must run inside the dedicated backend virtual environment (/home/idrees/job_agent/.venv/bin/python3)."

### Enki's Proposed Solution
Never invoke the naked `python3` command on PATH. Every script execution, test runner, and background worker must be explicitly invoked using `/home/idrees/job_agent/.venv/bin/python3` or the designated virtual environment path.

***

## 4. Complete Isolation from User Desktop Chrome Sessions

### Problem
Automation scripts attempted to connect to remote debugging port 9222 on the user's active personal Google Chrome instance, crashing desktop tabs and corrupting session cookies.

### Idrees's Solution
"Never attempt to attach to the user personal desktop Chrome browser or manipulate graphical debug ports."

### Enki's Proposed Solution
All browser automation must launch fully isolated headless Playwright browser binaries with temporary user data directories. Zero interaction with the user's desktop browser processes.

***

## 5. Mandatory Item Aggregation Before Outbound Notification Nodes

### Problem
An n8n workflow iterating over 5 scraped posts dispatched 5 individual Gmail messages back to back rather than combining the results into a single digest.

### Idrees's Solution
"it has written 5 times the same thing in the email, like 5 posts with upper line at same time, also I dont want to share the rating"

### Enki's Proposed Solution
Any n8n workflow that processes arrays of items must pass through an Item Lists node or a JavaScript Code node to aggregate items into a single payload before handing data to an email or messaging notification node.

***

## 6. Proper n8n JSON Export Schema Wrappers

### Problem
The model generated raw arrays containing only node definitions `[{...}]` without wrapping them in the canonical n8n clipboard export schema, causing n8n to reject the paste.

### Idrees's Solution
"n8n rejected the paste because n8n requires a top level wrapper object with "nodes": [...] and "connections": [...] now send again the testing for 2nd path"

### Enki's Proposed Solution
Every n8n workflow snippet or template generated for copy paste into the n8n canvas must provide the full canonical schema: `{"nodes": [...], "connections": {...}}`.

***

## 7. Elimination of Bare Except Blocks and Error Swallowing

### Problem
Python scripts in `execution/` utilized `except Exception: pass`, which masked critical network crashes, dropped scraped prospects silently, and prevented proper error escalation.

### Idrees's Solution
None provided by Idrees (Discovered during comprehensive code auditing).

### Enki's Proposed Solution
Strict prohibition of bare `except: pass` in production code. All exceptions must log the exact error message and traceback. When an unrecoverable failure occurs, the script must raise an exception or exit with a non zero status code so error catchers trigger.

***

## 8. Prohibition of Unsolicited Test Failure Injection

### Problem
The model programmatically modified an n8n workflow to force an intentional Google Sheets failure before the user had started recording their demonstration video.

### Idrees's Solution
"there was no execution in that workflow, dont do it right now do it again when I say there was no new submission or execution right now"

### Enki's Proposed Solution
Never trigger simulated faults or modify live workflows to cause errors without an explicit verbal command to begin the test sequence.
