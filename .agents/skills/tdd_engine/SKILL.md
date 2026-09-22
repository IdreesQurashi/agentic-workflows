---
name: tdd_engine
description: Enforces Test Driven Development with 80% plus test coverage, Red Green Refactor cycles, test runner detection, and verification evidence reporting.
---

# Test Driven Development Engine Skill

Use this skill when implementing new features, fixing bugs, or refactoring existing code. This skill enforces writing tests prior to code, proving the failure state, and achieving green verification.

## When to Activate
* Writing new functions, classes, or modules.
* Investigating and fixing reported bugs.
* Refactoring legacy or complex codebases.
* Following up after a specification plan has been approved.

## Core Rules
1. Never write application code without a pre existing failing test.
2. Achieve at least 80% test coverage across unit, integration, and user journey tests.
3. Every completed task must provide verifiable evidence with exit code 0.

## Procedure

### Step 1: Detect the Test Runner
Identify the native test runner in the workspace:
* Python: Inspect virtual environment for `pytest` or `unittest`.
* Node / TypeScript: Inspect `package.json` for Vitest, Jest, or native Bun test runner.
* Standalone execution scripts: Locate test fixtures in `execution/` or tests directory.

### Step 2: The RED Phase
1. Author test cases asserting desired behavior, boundary values, and error states.
2. Run the test runner to verify failure.
3. Confirm the test fails for the expected reason and not due to an environment or import error.
4. Record the failure output as RED evidence.

### Step 3: The GREEN Phase
1. Implement the minimal code necessary to make the failing test pass.
2. Avoid unnecessary speculative logic or extra features.
3. Run the test runner to verify green status with exit code 0.
4. Record the passing output as GREEN evidence.

### Step 4: The REFACTOR Phase
1. Clean the code for readability, maintainability, and algorithmic performance.
2. Remove dead code, redundant variables, and duplicated patterns.
3. Rerun the test runner after each edit to confirm zero regressions.

### Step 5: Checkpoint Commit
Record progress with an atomic Git commit documenting RED and GREEN evidence.
