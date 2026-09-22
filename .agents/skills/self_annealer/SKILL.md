---
name: self_annealer
description: Automatically captures execution failures, builds minimal reproducer scripts, patches tools, verifies fixes, and updates directives with permanent learnings.
---

# Self Annealer Skill

Use this skill whenever a script crashes, an API call fails, or an unexpected runtime exception halts execution. This skill orchestrates self healing and system hardening so the failure mode is permanently eliminated.

## When to Activate
* A script in `execution/` exits with a non zero status code.
* An external API throws a 429 rate limit, 401 auth error, or 500 server crash.
* A data pipeline receives unexpected formatting that breaks downstream parsing.

## Operating Invariant
Never patch code on intuition alone. Every fix must be verified against a standalone reproduction script before the change is committed.

## Step by Step Procedure

### Step 1: Parse the Error Vector
1. Extract the full standard error output and stack trace.
2. Identify the failing file, function, and exact line number.
3. Classify the error type: environmental, network, syntax, or logical.

### Step 2: Author Minimal Reproducer
1. Create a minimal standalone script at `.tmp/reproduce_error.py`.
2. Replicate only the exact inputs, parameters, and calls that produced the crash.
3. Execute `python3 .tmp/reproduce_error.py` and confirm the failure is faithfully reproduced.

### Step 3: Apply the Deterministic Patch
1. Modify the target script or configuration file to handle the failure vector.
2. Add explicit boundary validation, backoff delays, or error traps.
3. Ensure no backward compatibility issues are created.

### Step 4: Verify Against Reproducer
1. Execute `python3 .tmp/reproduce_error.py` again.
2. Confirm the script runs to completion with exit code 0.
3. Run the wider project test runner to confirm zero side regressions.
4. Clean up `.tmp/reproduce_error.py`.

### Step 5: Update Directive and Failure Registry
1. Open the governing SOP in `directives/` or the Master Operating Directive.
2. Record the failure, root cause, and permanent fix in the Failure Registry.
3. Update the directive instructions so future executions benefit from the learning.
