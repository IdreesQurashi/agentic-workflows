# Jev Router — Operator Runbook

**Workflow:** Router Shell v1 (Hardened Production)
**Instance:** https://n8n.srv1041226.hstgr.cloud
**Last Updated:** 2026-09-25

---

## 1. Checking Executions

1. Log in to n8n at the instance URL above
2. Click **Executions** in the left sidebar
3. Filter by workflow: select **Router Shell v1 (Hardened Production)**
4. Each row is one inbound message unit processed

**Reading a row:**
- Green circle = execution completed successfully
- Red circle = execution errored (check inside for which node failed)
- Run Time = total processing time from webhook receipt to ledger write
- Exec ID = unique identifier for this execution (use for failure reports)

**Opening an execution:**
Click any row to see the full node chain. Green nodes ran successfully. Red nodes errored. The last green node tells you which lane the unit reached.

---

## 2. Reading the Ledger

1. Click **Data Tables** in the left sidebar (or navigate via the workflow)
2. Open **Router Shell data table**
3. Each row = one processed unit written to the ledger

**Column meanings:**

| Column | Meaning |
|--------|---------|
| `unit_id` | Unique identifier of the message unit |
| `route` | Lane assigned: `auto_log`, `verify_queue`, `human_queue`, `dead_letter` |
| `label` | Classification returned by the AI (e.g. `billing`, `technical_support`) |
| `confidence` | AI confidence score (0.0 to 1.0) |
| `cost` | API call cost in USD |
| `ts` | Timestamp of when the unit was processed |
| `error` | Error detail if the unit went to dead letter (blank otherwise) |

**Filtering by lane:** Use the column filter on `route` to see only one lane at a time.

---

## 3. Lane Definitions (What Each Lane Means)

| Lane | Route Value | Meaning | Action Required |
|------|-------------|---------|----------------|
| Auto | `auto_log` | High confidence classification. AI is certain. | No human action needed. Logged for audit. |
| Verify | `verify_queue` | Medium confidence. AI made a call but is not certain. | Operator reviews and approves or overrides via action link. |
| Human | `human_queue` | Low confidence. AI cannot reliably classify. | Human agent handles this unit directly. |
| Dead Letter | `dead_letter` | Processing failed. API error or malformed input. | See Section 4 for replay procedure. |

---

## 4. Replaying a Dead Letter Unit

Use this when a unit landed in dead letter due to a temporary API failure and needs to be reprocessed.

1. Open the Data Table, filter `route = dead_letter`
2. Note the `unit_id` of the unit to replay
3. Send a POST request to the replay endpoint:

```
POST https://n8n.srv1041226.hstgr.cloud/webhook/replay-dead-letter

Body (JSON):
{
  "unit_id": "<the unit_id from the ledger>",
  "text": "<original message text>",
  "sender": "<original sender>"
}
```

4. Check the Executions tab — a new execution should appear within 5 seconds
5. Check the Data Table — confirm exactly ONE new ledger row was written (not a duplicate)
6. If a duplicate row appears, stop and escalate to the system owner. Do not replay again.

---

## 5. If the Workflow Stops Executing

Symptoms: messages are being sent but no new executions appear in the log.

**Check in order:**

1. Open the workflow in n8n editor
2. Check the header — confirm the **Active** toggle is ON (Published state, green dot)
3. If the toggle is OFF: do not activate without system owner approval. Log this as a blocker.
4. If the toggle is ON but executions still do not appear: check the **Executions** tab filter — make sure you are not filtering to a date range that excludes recent runs
5. Check the **HTTP: Decisions API** node for recent errors — if the AI provider is down, all units go to dead letter
6. Log the issue with: timestamp, last successful execution ID, first failed execution ID, and any error message visible in the execution detail view

---

## 6. Escalation

All workflow changes, credential updates, threshold adjustments, and lane schema changes require system owner approval before implementation. Log any issue and wait for ruling before making modifications.

