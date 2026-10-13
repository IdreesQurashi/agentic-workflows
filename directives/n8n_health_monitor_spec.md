# n8n Health Monitor Workflow Specification

## 1. System Overview
The n8n Health Monitor is a production-grade automated workflow scheduled to audit the operational health of an n8n instance every 24 hours. It queries the n8n Public API, aggregates key operational metrics, detects failed executions, formats an actionable HTML status report, and dispatches it via Gmail to designated engineers.

## 2. Core Functional Requirements
1. **Schedule Trigger:** Triggers daily at 08:00 AM UTC.
2. **Active Workflows Audit:** Queries `GET /api/v1/workflows` to identify active versus inactive workflows and count total production automations.
3. **24-Hour Execution Audit:** Queries `GET /api/v1/executions` within a strict 24-hour UTC window (`startedAfter = $now.toUTC().minus({ hours: 24 }).toISO()`).
4. **Zero-Memory-Bloat Querying:** Enforces `includeData=false` on all execution queries, preventing Node.js heap memory exhaustion.
5. **Execution Circuit Breaker:** Implements page-limit safety (up to 1,000 runs) to protect n8n internal database query performance.
6. **Detailed Error Trace Extraction:** For failed executions, queries single execution error metadata (`GET /api/v1/executions/{id}?includeData=true`) for the top 5 failures to extract the failing node name and error message.
7. **Actionable Deep Links:** Generates direct, external URLs (`https://[host]/workflow/[workflowId]/executions/[executionId]`) allowing one-click incident triage.
8. **Conditional Alert Routing:**
   * If `failedCount > 0`: Dispatches an `🚨 URGENT: n8n Instance Health Alert` with a red priority banner and failure breakdown table.
   * If `failedCount == 0`: Dispatches a `✅ [n8n Report] All Systems Healthy` green operational digest.
9. **Recipient:** `idreesqurashi.ai@gmail.com` via native n8n Gmail OAuth2 credential.

## 3. Node Architecture & Data Flow

```
[Schedule Trigger (08:00 Daily)]
               │
               ▼
[Config & Time Window Setup] (Code Node)
   - startedAfter: 24h UTC ISO string
   - startedBefore: Current UTC ISO string
   - baseUrl: http://localhost:5678
   - externalUrl: http://localhost:5678
   - recipient: idreesqurashi.ai@gmail.com
               │
       ┌───────┴────────────────────────┐
       ▼                                ▼
[HTTP: Get Workflows]         [HTTP: Get 24h Executions]
 GET /api/v1/workflows         GET /api/v1/executions
 (Active vs Inactive list)     (includeData=false, limit=250)
       └───────┬────────────────────────┘
               ▼
[Metrics Aggregator & Error Inspector] (Code Node)
   - Computes: Total, Active, Inactive, Success, Failed
   - Fetches / parses top failure details
   - Builds responsive HTML email template
               │
               ▼
[If: Failures > 0]
      ├── TRUE  ──► [Gmail: Send URGENT Alert Email]
      └── FALSE ──► [Gmail: Send Daily Health Digest Email]
```

## 4. API Endpoints Contract
* `GET /api/v1/workflows`: Returns JSON array of all registered workflows.
* `GET /api/v1/executions?startedAfter={ISO}&includeData=false&limit=250`: Returns execution metadata.
* `GET /api/v1/executions/{id}?includeData=true`: Used selectively only for failed runs to pull `resultData.error.message`.
