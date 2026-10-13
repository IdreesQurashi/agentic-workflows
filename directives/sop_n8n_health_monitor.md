# Standard Operating Procedure (SOP)
# Building the n8n Instance Daily Health Monitor in Under 1 Hour

**Document Target:** Junior AI Automation Engineer / Technical Operator  
**Prerequisites:** Basic familiarity with n8n UI, web browser, Google account.  
**Estimated Rebuild Time:** 35 to 45 minutes  
**Goal:** Deploy an automated daily workflow that audits active workflows, counts 24h executions, detects errors, and emails an actionable HTML health alert to `idreesqurashi.ai@gmail.com`.

---

## Architecture Diagram

```
+-------------------------------------------------------------------------------------------------+
|                                 n8n DAILY HEALTH MONITOR PIPELINE                               |
+-------------------------------------------------------------------------------------------------+
|                                                                                                 |
|  [01. Schedule Trigger]                                                                         |
|        Daily at 08:00 AM UTC                                                                    |
|                 │                                                                               |
|                 ▼                                                                               |
|  [02. Set Config & 24h Window] ──► Sets startedAfter (UTC ISO), Base URL, Recipient             |
|                 │                                                                               |
|                 ▼                                                                               |
|  [03A. Fetch Workflows] ──► GET /api/v1/workflows (Reads all workflows)                         |
|                 │                                                                               |
|                 ▼                                                                               |
|  [03B. Fetch 24h Executions] ──► GET /api/v1/executions (includeData=false, limit=250)         |
|                 │                                                                               |
|                 ▼                                                                               |
|  [04. Aggregate Metrics & Format HTML]                                                          |
|   JavaScript Code Node: Calculates success rate, compiles failures, builds responsive HTML      |
|                 │                                                                               |
|                 ▼                                                                               |
|  [05. Check If Failures Exist]                                                                  |
|   Condition: failedCount > 0 ?                                                                  |
|        ├── TRUE  ──► [06A. Gmail: Send URGENT Failure Alert (Red Banner + Direct Links)]        |
|        └── FALSE ──► [06B. Gmail: Send Clean Health Digest (Green Banner + Zero Errors)]        |
|                                                                                                 |
+-------------------------------------------------------------------------------------------------+
```

---

## ⚡ Quick-Deploy Option: Deploy Anywhere in Under 10 Minutes

If you already have an n8n instance and want to deploy this monitoring system in **under 10 minutes** without building node-by-node:

1. **Step 1: Import Workflow JSON (1 Minute)**
   * Open your n8n canvas ➔ Click the `...` menu in the top right ➔ Select **Import from File**.
   * Select [`execution/workflows/n8n_health_monitor_workflow.json`](file:///home/idrees/Antigravity/Agentic%20Workflows-20260907T212811Z-1-001/Agentic%20Workflows/execution/workflows/n8n_health_monitor_workflow.json).
2. **Step 2: Generate API Key (2 Minutes)**
   * Go to `Settings > Public API` ➔ Click **Create an API Key** ➔ Copy the token.
3. **Step 3: Update Config Node (2 Minutes)**
   * Double-click `Set Config & 24h Window` and update three fields:
     * `baseUrl`: Your internal n8n URL (e.g. `http://localhost:5678` or `http://n8n:5678`).
     * `externalBaseUrl`: Your public n8n URL (e.g. `https://n8n.yourcompany.com`).
     * `n8nApiKey`: Paste the API key generated in Step 2.
     * `recipientEmail`: Your alert email (e.g. `idreesqurashi.ai@gmail.com`).
4. **Step 4: Select Gmail Credential (2 Minutes)**
   * Double-click `Send Urgent Failure Alert` and `Send Clean Health Digest` ➔ Select your connected Gmail account from the dropdown.
5. **Step 5: Activate Workflow (1 Minute)**
   * Click **Execute workflow** to verify test run ➔ Toggle **Published / Active** in the top right corner. Done!

---

## Complete Scratchpad Rebuild: Manual Step-by-Step SOP (Under 1 Hour)

Before creating the workflow, you must establish two credentials inside n8n:
1. An **n8n Public API Key** (to read internal workflow and execution data).
2. A **Gmail Account Credential** (to dispatch email alerts).

### Step 1.1: Generate an n8n Public API Key
1. Open your n8n web dashboard (`http://localhost:5678` or your domain).
2. Click on **Settings** in the bottom left sidebar (gear icon).
3. Under the *Instance* or *Admin* section, click on **Public API**.
4. Click the orange **Create an API Key** button.
5. In the modal, provide a descriptive label: `Health Monitor Auditor`.
6. Set expiration according to your security policy (or select *Never Expire* for internal production).
7. Click **Create**.
8. **CRITICAL:** Copy the generated token immediately. Save it in your password manager or `.env` file. You will not be able to view it again.

```
+------------------------------------------------------------------+
| Settings > Public API                                            |
|                                                                  |
| Key Name: Health Monitor Auditor                                 |
| Token:    YOUR_N8N_API_KEY_PLACEHOLDER                |
|                                                                  |
| [Copy API Key]  [Done]                                           |
+------------------------------------------------------------------+
[Screenshot Reference: Step_1.1_Create_n8n_API_Key.png]
```

### Step 1.2: Connect Your Gmail Account
1. In the n8n left sidebar, click on **Credentials**.
2. Click the orange **Add Credential** button in the top right.
3. In the search box, type `Gmail` and select **Gmail OAuth2 API**.
4. Click **Connect my account** (or follow the Google Cloud OAuth instructions if using custom client ID).
5. Authenticate with your designated alert sender account (e.g. `idreesqurashi.ai@gmail.com`).
6. Grant n8n permissions to send emails on your behalf.
7. Click **Save** and verify the green *Connected* badge appears.

```
+------------------------------------------------------------------+
| Credentials > New Credential > Gmail OAuth2 API                  |
|                                                                  |
| Credential Name: Gmail account                                   |
| Status:          Connected (Green Checkmark)                     |
|                                                                  |
| [Save]                                                           |
+------------------------------------------------------------------+
[Screenshot Reference: Step_1.2_Connect_Gmail_OAuth.png]
```

---

## Phase 2: Workflow Assembly (20 Minutes)

### Step 2.1: Create a New Blank Workflow
1. In the left sidebar, click **Workflows** > **Add Workflow**.
2. Click on the title in the top header and rename it to: `n8n Daily Instance Health Monitor`.
3. Save the workflow using `Ctrl + S` or the save icon.

---

### Step 2.2: Add Node 1 — Schedule Trigger
1. Click the `+` button in the canvas center to add your first node.
2. Search for `Schedule` and select **Schedule Trigger**.
3. Configure the trigger parameters:
   * **Trigger Interval:** `Weeks` or `Days`
   * **Run Every:** `1 Day`
   * **At Hour:** `8` (08:00 AM)
   * **At Minute:** `0`
4. Rename this node: `Schedule Daily 08:00 AM`.

```
[Screenshot Reference: Step_2.2_Schedule_Trigger_Config.png]
```

---

### Step 2.3: Add Node 2 — Set Config & 24h Window (Code Node)
1. Add a **Code** node and connect it to the Schedule Trigger.
2. Set **Language:** `JavaScript`.
3. Paste the following exact script into the code box:

```javascript
const now = new Date();
const past24h = new Date(now.getTime() - (24 * 60 * 60 * 1000));

return [{
  json: {
    startedAfter: past24h.toISOString(),
    startedBefore: now.toISOString(),
    baseUrl: 'http://localhost:5678',
    externalBaseUrl: 'http://localhost:5678',
    recipientEmail: 'idreesqurashi.ai@gmail.com'
  }
}];
```
4. Rename this node: `Set Config & 24h Window`.
5. Click **Test step** to verify it outputs the timestamps and config fields.

```
[Screenshot Reference: Step_2.3_Config_Code_Node.png]
```

---

### Step 2.4: Add Node 3A — Fetch Workflows (HTTP Request)
1. Add an **HTTP Request** node and connect it to `Set Config & 24h Window`.
2. Configure parameters:
   * **Method:** `GET`
   * **URL:** `={{ $json.baseUrl }}/api/v1/workflows`
   * **Send Headers:** `Toggle ON`
   * Under **Header Parameters**, click **Add Parameter**:
     * **Name:** `X-N8N-API-KEY`
     * **Value:** Paste your n8n API Key (or expression `={{ $env.N8N_API_KEY }}`)
3. Rename this node: `Fetch Workflows`.
4. Click **Test step**. You should receive a JSON response containing an array `data` with all registered workflows.

```
[Screenshot Reference: Step_2.4_Fetch_Workflows_HTTP.png]
```

---

### Step 2.5: Add Node 3B — Fetch 24h Executions (HTTP Request)
1. Add a second **HTTP Request** node and connect it to the output of `Fetch Workflows`.
2. Configure parameters:
   * **Method:** `GET`
   * **URL:** `={{ $('Set Config & 24h Window').first().json.baseUrl }}/api/v1/executions`
   * **Send Query Parameters:** `Toggle ON`
   * Add 3 Query Parameters:
     1. Name: `startedAfter` | Value: `={{ $('Set Config & 24h Window').first().json.startedAfter }}`
     2. Name: `includeData` | Value: `false` *(CRITICAL: Prevents memory exhaustion)*
     3. Name: `limit` | Value: `250`
   * **Send Headers:** `Toggle ON`
   * Under **Header Parameters**:
     * **Name:** `X-N8N-API-KEY`
     * **Value:** Paste your n8n API Key
3. Rename this node: `Fetch 24h Executions`.
4. Click **Test step** to verify execution metadata is returned.

```
[Screenshot Reference: Step_2.5_Fetch_Executions_HTTP.png]
```

---

### Step 2.6: Add Node 4 — Aggregate Metrics & Format HTML (Code Node)
1. Add a **Code** node and connect it to the output of `Fetch 24h Executions`.
2. Set **Language:** `JavaScript`.
3. Paste the following aggregator and HTML builder script:

```javascript
const config = $('Set Config & 24h Window').first().json;
const workflowsData = $('Fetch Workflows').first().json.data || [];
const executionsData = $('Fetch 24h Executions').first().json.data || [];

const totalWorkflows = workflowsData.length;
const activeWorkflows = workflowsData.filter(w => w.active === true);
const inactiveWorkflows = workflowsData.filter(w => !w.active);

const workflowMap = {};
workflowsData.forEach(w => {
  workflowMap[w.id] = w.name;
});

const totalRecordedExecutions = executionsData.length;
const failedExecutions = executionsData.filter(e => e.status === 'error' || e.finished === false);
const successfulExecutions = executionsData.filter(e => e.status === 'success');

const failedCount = failedExecutions.length;
const successCount = successfulExecutions.length;
const successRate = totalRecordedExecutions > 0 
  ? ((successCount / totalRecordedExecutions) * 100).toFixed(1) 
  : '100.0';

const failuresSummary = failedExecutions.slice(0, 10).map(e => {
  const wfName = workflowMap[e.workflowId] || 'Unknown Workflow';
  const execUrl = `${config.externalBaseUrl}/workflow/${e.workflowId}/executions/${e.id}`;
  return {
    id: e.id,
    workflowId: e.workflowId,
    workflowName: wfName,
    startedAt: e.startedAt,
    status: e.status,
    executionUrl: execUrl
  };
});

const isUrgent = failedCount > 0;
const statusBadge = isUrgent ? 'CRITICAL - ACTION REQUIRED' : 'HEALTHY - ALL SYSTEMS GO';
const statusColor = isUrgent ? '#dc2626' : '#16a34a';
const statusBg = isUrgent ? '#fee2e2' : '#dcfce7';

let failureRowsHtml = '';
if (failuresSummary.length > 0) {
  failureRowsHtml = failuresSummary.map(f => `
    <tr style="border-bottom: 1px solid #e5e7eb;">
      <td style="padding: 10px; font-weight: 600; color: #1f2937;">${f.workflowName}</td>
      <td style="padding: 10px; color: #4b5563;">#${f.id}</td>
      <td style="padding: 10px; color: #6b7280; font-size: 13px;">${new Date(f.startedAt).toLocaleString()}</td>
      <td style="padding: 10px; text-align: right;">
        <a href="${f.executionUrl}" style="background-color: #dc2626; color: #ffffff; padding: 6px 12px; text-decoration: none; border-radius: 4px; font-size: 12px; font-weight: 500;" target="_blank">Inspect Failure</a>
      </td>
    </tr>
  `).join('');
} else {
  failureRowsHtml = '<tr><td colspan="4" style="padding: 16px; text-align: center; color: #16a34a; font-weight: 500;">Zero failures recorded in the past 24 hours.</td></tr>';
}

const activeWfListHtml = activeWorkflows.slice(0, 15).map(w => `
  <li style="padding: 4px 0; color: #374151; font-size: 14px;">
    <strong>${w.name}</strong> <span style="color: #9ca3af; font-size: 12px;">(${w.id})</span>
  </li>
`).join('');

const htmlEmail = `
<!DOCTYPE html>
<html>
<head>
  <meta charset="utf-8">
  <title>n8n Instance Health Report</title>
</head>
<body style="font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Helvetica, Arial, sans-serif; background-color: #f3f4f6; margin: 0; padding: 20px; color: #1f2937;">
  <div style="max-width: 680px; margin: 0 auto; background: #ffffff; border-radius: 8px; overflow: hidden; border: 1px solid #e5e7eb; box-shadow: 0 1px 3px rgba(0,0,0,0.1);">
    
    <div style="background-color: ${statusColor}; padding: 20px 24px; color: #ffffff;">
      <h1 style="margin: 0; font-size: 20px; font-weight: 700; letter-spacing: -0.025em;">
        ${isUrgent ? '🚨 URGENT: n8n Instance Health Alert' : '✅ n8n Instance Daily Health Report'}
      </h1>
      <p style="margin: 6px 0 0 0; font-size: 14px; opacity: 0.9;">
        Reporting Window: Last 24 Hours &bull; Audited on ${new Date().toUTCString()}
      </p>
    </div>

    <div style="padding: 24px;">
      <div style="display: inline-block; padding: 6px 12px; border-radius: 9999px; background-color: ${statusBg}; color: ${statusColor}; font-weight: 700; font-size: 13px; text-transform: uppercase; margin-bottom: 20px;">
        ${statusBadge}
      </div>

      <div style="display: grid; grid-template-columns: repeat(4, 1fr); gap: 12px; margin-bottom: 24px;">
        <div style="background: #f9fafb; border: 1px solid #e5e7eb; border-radius: 6px; padding: 12px; text-align: center;">
          <div style="font-size: 11px; text-transform: uppercase; color: #6b7280; font-weight: 600;">Active Flows</div>
          <div style="font-size: 22px; font-weight: 700; color: #111827; margin-top: 4px;">${activeWorkflows.length}</div>
          <div style="font-size: 11px; color: #9ca3af;">of ${totalWorkflows} total</div>
        </div>
        <div style="background: #f9fafb; border: 1px solid #e5e7eb; border-radius: 6px; padding: 12px; text-align: center;">
          <div style="font-size: 11px; text-transform: uppercase; color: #6b7280; font-weight: 600;">Recorded Runs</div>
          <div style="font-size: 22px; font-weight: 700; color: #111827; margin-top: 4px;">${totalRecordedExecutions}</div>
          <div style="font-size: 11px; color: #9ca3af;">past 24h</div>
        </div>
        <div style="background: #f9fafb; border: 1px solid #e5e7eb; border-radius: 6px; padding: 12px; text-align: center;">
          <div style="font-size: 11px; text-transform: uppercase; color: #6b7280; font-weight: 600;">Success Rate</div>
          <div style="font-size: 22px; font-weight: 700; color: #16a34a; margin-top: 4px;">${successRate}%</div>
          <div style="font-size: 11px; color: #9ca3af;">${successCount} passed</div>
        </div>
        <div style="background: ${isUrgent ? '#fee2e2' : '#f9fafb'}; border: 1px solid ${isUrgent ? '#fca5a5' : '#e5e7eb'}; border-radius: 6px; padding: 12px; text-align: center;">
          <div style="font-size: 11px; text-transform: uppercase; color: ${isUrgent ? '#991b1b' : '#6b7280'}; font-weight: 600;">Failed Runs</div>
          <div style="font-size: 22px; font-weight: 700; color: ${isUrgent ? '#dc2626' : '#111827'}; margin-top: 4px;">${failedCount}</div>
          <div style="font-size: 11px; color: ${isUrgent ? '#b91c1c' : '#9ca3af'};">urgent review</div>
        </div>
      </div>

      <h2 style="font-size: 16px; font-weight: 700; margin: 24px 0 12px 0; border-bottom: 2px solid #f3f4f6; padding-bottom: 6px;">
        ${isUrgent ? '⚠️ Recent Failed Executions (Top ' + failuresSummary.length + ')' : 'Execution Health Status'}
      </h2>
      <table style="width: 100%; border-collapse: collapse; font-size: 14px; margin-bottom: 24px;">
        <thead>
          <tr style="background-color: #f9fafb; text-align: left; color: #6b7280; font-size: 12px; text-transform: uppercase; border-bottom: 1px solid #e5e7eb;">
            <th style="padding: 10px;">Workflow</th>
            <th style="padding: 10px;">Exec ID</th>
            <th style="padding: 10px;">Timestamp</th>
            <th style="padding: 10px; text-align: right;">Action</th>
          </tr>
        </thead>
        <tbody>
          ${failureRowsHtml}
        </tbody>
      </table>

      <h2 style="font-size: 16px; font-weight: 700; margin: 24px 0 12px 0; border-bottom: 2px solid #f3f4f6; padding-bottom: 6px;">
        Active Production Workflows (${activeWorkflows.length})
      </h2>
      <ul style="margin: 0; padding-left: 20px; line-height: 1.6;">
        ${activeWorkflows.length > 0 ? activeWfListHtml : '<li style="color: #6b7280;">No workflows currently active.</li>'}
      </ul>
    </div>

    <div style="background: #f9fafb; border-top: 1px solid #e5e7eb; padding: 14px 24px; font-size: 12px; color: #6b7280; text-align: center;">
      Generated autonomously by n8n Health Monitor &bull; Instance: ${config.baseUrl}
    </div>
  </div>
</body>
</html>
`;

const subject = isUrgent
  ? `🚨 URGENT: [n8n Alert] ${failedCount} Failed Executions Detected in Last 24h`
  : `✅ [n8n Report] All Systems Healthy (${activeWorkflows.length} Active Workflows)`;

return [{
  json: {
    isUrgent,
    failedCount,
    successCount,
    totalRecordedExecutions,
    activeWorkflowsCount: activeWorkflows.length,
    totalWorkflowsCount: totalWorkflows,
    subject,
    htmlEmail,
    recipientEmail: config.recipientEmail
  }
}];
```
4. Rename this node: `Aggregate Metrics & Format HTML`.
5. Click **Test step** to verify proper HTML assembly.

```
[Screenshot Reference: Step_2.6_Aggregate_Metrics_Code.png]
```

---

### Step 2.7: Add Node 5 — Check If Failures Exist (If Node)
1. Add an **If** node and connect it to `Aggregate Metrics & Format HTML`.
2. Configure condition:
   * **Value 1:** `={{ $json.failedCount }}`
   * **Operation:** `is greater than` (number)
   * **Value 2:** `0`
3. Rename this node: `Check If Failures Exist`.
4. This node has two outputs:
   * **True output:** Routes to the Urgent Alert branch.
   * **False output:** Routes to the Clean Health Digest branch.

```
[Screenshot Reference: Step_2.7_If_Condition_Branching.png]
```

---

### Step 2.8: Add Node 6A & 6B — Gmail Dispatch Nodes
1. Add a **Gmail** node and connect it to the **True** output of the If node.
   * **Credential to connect with:** Select your `Gmail account`.
   * **Resource:** `Message`
   * **Operation:** `Send`
   * **To:** `={{ $json.recipientEmail }}`
   * **Subject:** `={{ $json.subject }}`
   * **Email Type:** `HTML`
   * **Message:** `={{ $json.htmlEmail }}`
   * Rename node: `Send Urgent Failure Alert`.
2. Add a second **Gmail** node and connect it to the **False** output of the If node.
   * Configure with identical parameters:
     * **To:** `={{ $json.recipientEmail }}`
     * **Subject:** `={{ $json.subject }}`
     * **Email Type:** `HTML`
     * **Message:** `={{ $json.htmlEmail }}`
   * Rename node: `Send Clean Health Digest`.
3. Save your workflow.

```
[Screenshot Reference: Step_2.8_Gmail_Dispatch_Nodes.png]
```

---

## Phase 3: Testing & Verification (15 Minutes)

### Step 3.1: Verify Clean State Execution
1. Click **Test workflow** in the canvas header.
2. Watch the execution light up green across all nodes.
3. Check the If node: it should evaluate to `False` (if 0 failures exist in the last 24h).
4. Verify your inbox at `idreesqurashi.ai@gmail.com`: you will receive the clean green email digest.

* **Canvas Execution Reference:** `directives/screenshots/09_v2_canvas_with_filters_clean_branch.png`
* **Clean Email Alert Reference:** `directives/screenshots/11_gmail_clean_digest_received.png`

---

### Step 3.2: Force a Failure & Verify Urgent Alert
To prove that the alert rule functions properly in production, simulate an intentional crash:
1. Create a dummy workflow named `Test Crash Generator` (or `Forced Failure Simulation Worker`).
2. Add a **Manual Trigger** node.
3. Connect a **Code** node with:
   ```javascript
   throw new Error("Simulated Production Outage: Warehouse API 500 Server Error");
   ```
4. Click **Test step** in the dummy workflow to trigger an error execution in n8n's database.
   * **Simulation Worker Reference:** `directives/screenshots/04_forced_failure_simulation_worker.png`
5. Return to `n8n Daily Instance Health Monitor` and click **Test workflow**.
6. Observe that `Check If Failures Exist` evaluates to `True`.
   * **Urgent Canvas Execution Reference:** `directives/screenshots/08_v2_canvas_with_filters_urgent_branch.png`
7. Inspect the email received:
   * Subject line prefixed with `🚨 URGENT: [n8n Alert]`
   * Red header banner (`CRITICAL - ACTION REQUIRED`)
   * Direct deep-link button pointing to the exact failed execution log.
   * **Urgent Email Alert Reference:** `directives/screenshots/10_gmail_urgent_alert_received.png` and `directives/screenshots/12_gmail_urgent_alert_detailed_view.png`

---

## Phase 4: Production Activation (2 Minutes)

1. In the top right corner of the workflow editor, toggle the switch from **Inactive** to **Active**.
2. Click **Save**.
3. The health monitor is now fully operational and will execute autonomously every morning at 08:00 AM UTC.

---

## Phase 5: Production Noise Filtration (Separating Test Runs from Real Failures)

When building and testing inside the n8n canvas, manual test runs can generate dozens of test errors. To prevent alert fatigue, the workflow includes two specialized filter modules:

### Method 1: Production Triggers Only (`mode !== 'manual'`)
* **Node Name:** `Filter Method 1: Production Triggers Only`
* **Mechanism:** n8n automatically stamps each execution with its execution trigger mode:
  * `manual` ➔ Triggered by a developer inside the workflow editor (testing).
  * `trigger` ➔ Triggered autonomously on a scheduled timer or cron.
  * `webhook` ➔ Triggered by an external HTTP incoming payload.
* **Code Implementation:**
  ```javascript
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
  }];
  ```
* **Operational Benefit:** Developers can run experimental manual tests in the canvas without triggering false positive urgent alerts.

---

### Method 2: Active Workflows Only (`active === true`)
* **Node Name:** `Filter Method 2: Active Workflows Only`
* **Mechanism:** Filters out draft and scratchpad workflows that are toggled off (`active: false`), focusing strictly on live published automations.
* **Code Implementation:**
  ```javascript
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
  }];
  ```
* **Operational Benefit:** Experimental, unactivated workflows never pollute production health metrics.

---

## Troubleshooting & Common Pitfalls

| Problem | Root Cause | Solution |
| :--- | :--- | :--- |
| **HTTP Request returns 401 Unauthorized** | Missing or invalid API key in headers. | Check `X-N8N-API-KEY` header in nodes 3A and 3B. Regenerate API key in `Settings > Public API`. |
| **HTTP Request returns ECONNREFUSED** | `baseUrl` cannot resolve `localhost` inside Docker container. | Change `baseUrl` in Node 2 to `http://host.docker.internal:5678` or use your public n8n domain. |
| **Gmail node throws Insufficient Permissions** | Google OAuth scope did not grant send permissions. | Reconnect Gmail credential in n8n and accept the permission checkbox for sending emails. |
| **Executions count shows zero despite recent runs** | Timezone mismatch in timestamp filter. | Ensure `startedAfter` uses `.toISOString()`, which forces UTC standard ISO formatting matching n8n's database. |
| **Canvas test errors triggering alerts** | Developer manual runs included in audit. | Connect `Filter Method 1` to isolate `mode !== 'manual'` runs before evaluation. |

