# T3 Lane Verification Checklist
**Date:** 2026-09-25
**Harness Run Used:** run_20260925_044348.json

| # | Fixture | HTTP | Execution | Lane Reached | Ledger Row | Pass/Fail |
|---|---------|------|-----------|-------------|------------|-----------|
| 1 | C1-01 auto | 202 | 24951 | Pending screenshot | Pending | Pending |
| 2 | C1-02 auto | 202 | 24952 | Pending screenshot | Pending | Pending |
| 3 | C1-03 auto | 202 | 24953 | Pending screenshot | Pending | Pending |
| 4 | C1-04 auto | 202 | 24954 | Pending screenshot | Pending | Pending |
| 5 | C2-01 verify | 202 | 24955 | Pending screenshot | Pending | Pending |
| 6 | C2-02 verify | 202 | 24956 | Pending screenshot | Pending | Pending |
| 7 | C2-03 verify | 202 | 24957 | Pending screenshot | Pending | Pending |
| 8 | C3-01 human | 202 | 24958 | Pending screenshot | Pending | Pending |
| 9 | C3-02 human | 202 | 24959 | Pending screenshot | Pending | Pending |
| 10 | C3-03 human | 202 | 24960 | Pending screenshot | Pending | Pending |
| 11 | C4-01 boundary 0.85 | 202 | 24961 | Pending screenshot | Pending | Pending |
| 12 | C4-02 boundary 0.50 | 202 | 24962 | Pending screenshot | Pending | Pending |
| 13 | C4-03 boundary 0.4999 | 202 | 24963 | Pending screenshot | Pending | Pending |
| 14 | C5-01 malformed | 422 | N/A (rejected at webhook) | dead_letter (webhook) | N | PASS |
| 15 | C5-02 missing unit_id | 202 | 24964 | Pending screenshot | Pending | Pending |
| 16 | C5-03 wrong type | 202 | 24965 | Pending screenshot | Pending | Pending |
| 17 | C6-01 oversized | 202 | 24966 | Pending screenshot | Pending | Pending |
| 18 | C7-01 empty text | 202 | 24967 | Pending screenshot | Pending | Pending |
| 19 | C7-02 whitespace | 202 | 24968 | Pending screenshot | Pending | Pending |
| 20 | C8-01 dup ID first | 202 | 24969 | Pending screenshot | Y | Pending |
| 21 | C8-02 dup ID second | 202 | 24970 | Pending screenshot | Y (duplicate — FAIL-005) | FAIL |

**Screenshots required:** evidence/T3/ folder. One per execution class minimum.
