# High Velocity Operations Copilot Directive

## 1. Directive Scope & Objective
Define standard operating procedures for live 2 hour client operational shifts, ensuring zero communication drift, plan first governance, and auditable proof of work.

## 2. Core Execution Invariants
* Plan First Locking: Prior to writing code or modifying workflows, author a structured sprint plan and persist it to local storage.
* ISO Timestamp Step Evidence: Every critical state transition, API call, and script execution must be recorded with full ISO 8601 timestamps and status codes.
* Corporate Jargon Scrubber: Automatically purge conversational filler, defensive apologies, and corporate buzzwords from outgoing client updates. State technical reality directly.
* 11:55 AM Hard Stop: Trigger the end of sprint compilation 5 minutes prior to shift completion. Automatically synthesize the 5 line Loom walkthrough script and format the daily handover report.
* Dual Documents Export: Always persist artifacts to local disk storage (`Documents/MAK_DAILY_REPORT.txt` and `Documents/MAK_PLAN_FIRST.txt`) ensuring client visibility independent of terminal context.

## 3. Operational Timeline
1. 10:00 AM: Initialize session and load current sprint targets.
2. 10:05 AM: Lock Plan First document with step estimates.
3. 10:05 AM to 11:50 AM: Execute deterministic technical tasks with live evidence logging.
4. 11:55 AM: Hard stop trigger activates. Generate Loom walkthrough script and client handover report.
