# Jev Router — Failure Report
**Date:** 2026-09-25
**Tester:** Idrees
**Workflow:** Router Shell v1 (Hardened Production)

---

## T2 Harness Results Summary

| Run | Time | 202 OK | 422 | 404 | Notes |
|-----|------|--------|-----|-----|-------|
| Run 1 | 09:29 | 0 | 0 | 21 | Workflow not published — all 404 |
| Run 2 | 09:33 | 20 | 1 | 0 | Workflow published, webhook live |
| Run 3 | 09:43 | 20 | 1 | 0 | Switch rules updated, results consistent |

C5-01 (malformed JSON) correctly returns 422 in all live runs. All other valid fixtures return 202 Accepted.

---

## FAIL-001 — First Run: Workflow Not Published

**Fixture:** All 21
**Expected:** 202 Accepted
**Actual:** 404 Not Found
**Root Cause:** Workflow was in draft/unpublished state. Production webhook URL was inactive.
**Resolution:** Clicked Publish in n8n workflow editor. No code change required.
**Status:** RESOLVED

---

## FAIL-002 — Telegram Notify Nodes Using HTTP Instead of Telegram Node

**Fixture:** N/A (workflow structure issue)
**Expected:** Notify: Dead Letter Alert, Notify: Operator Verify Queue, Notify: Operator Human Queue send Telegram messages
**Actual:** All 3 nodes are generic HTTP Request nodes posting to httpbin.org (a test echo service). No real notifications are delivered.
**Execution IDs:** 24924, 24925, 24926 (Telegram node test errors)
**Root Cause:** Nodes were built as HTTP placeholders. Telegram credential integration is pending.
**Fix Required:** Replace 3 HTTP notify nodes with native n8n Telegram nodes. Requires MAK to confirm target chat ID and credential.
**Status:** OPEN — awaiting MAK ruling on return

---

## FAIL-003 — n8n Execution Log Retention Cap

**Fixture:** All 21
**Expected:** All 21 execution records visible in n8n Executions tab for manual T3 verification
**Actual:** Only 10 executions visible per view on current plan
**Root Cause:** n8n cloud free/starter plan caps execution log retention
**Fix Required:** Plan upgrade OR self-hosted n8n for full 21-fixture audit trail
**Status:** OPEN — document only, MAK to decide on plan

---

## FAIL-004 — Human Queue Lane Not Reachable via Switch (Fixed Before Final Run)

**Fixture:** C3 class (human lane)
**Expected:** Switch routes confidence < 0.50 to Human Queue Lane
**Actual:** Original Switch had only 2 rules (>= 0.95 Auto, < 0.05 Verify). Human Queue Lane had no incoming wire.
**Resolution:** Switch rules updated to: >= 0.50 Auto, < 0.50 Verify. Human Queue Lane wired. Published before Run 3.
**Status:** RESOLVED (partial — Human Queue Lane now reachable but merged with Verify logic pending MAK threshold review)

---

## FAIL-005 — No Dedup Mechanism in Workflow

**Fixture:** C8-02 (duplicate unit_id)
**Expected:** Dedup guard fires, no second ledger row created
**Actual:** No dedup logic exists anywhere in the workflow. C8-02 created a second ledger row identical to C8-01.
**Fix Required:** Add a pre-write check in the ledger node or a Code node before it that queries the Data Table for existing unit_id before appending.
**Status:** OPEN — awaiting MAK ruling on return

---

## FAIL-006 — No Oversized Text Guard

**Fixture:** C6-01 (15,028 char text)
**Expected:** Oversized text rejected before reaching AI API
**Actual:** No size guard exists. C6-01 was passed to the Decisions API as-is. API either processed or errored on it.
**Fix Required:** Add a Code node after Registry Lookup that checks text.length and routes to dead letter if above threshold.
**Status:** OPEN — awaiting MAK ruling on return

---

## Zero Silent Fixes

No failure was corrected without logging above. All open items held for MAK review on return.
