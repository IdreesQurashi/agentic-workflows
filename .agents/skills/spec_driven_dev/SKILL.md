---
name: spec_driven_dev
description: Enforces Spec Driven Development by drafting PRD specifications, resolving ambiguity, authoring technical blueprints, and decomposing atomic task checklists before writing code.
---

# Spec Driven Development Skill

Use this skill when developing new features, creating major architectural enhancements, or executing complex multi file refactors. It enforces that intent and specifications are codified before implementation begins.

## When to Activate
* Starting a new feature, module, or integration.
* The user prompt presents a high level or ambiguous requirement.
* Moving from concept to structured execution without vibe coding.

## Procedure

### Step 1: Capture Specification
Draft a specification containing:
1. Problem Statement: The exact friction or system need being solved.
2. User Journeys: Formulate journeys in the standard structure: As a role, I want action, so that benefit.
3. System Invariants: Non negotiable constraints, guarantees, and boundaries.
4. Acceptance Criteria: Binary observable criteria required to consider the feature complete.

### Step 2: Adversarial Ambiguity Audit
Review the specification with an adversarial lens:
1. Probe edge cases: empty payloads, network disconnects, rate limits, invalid typings.
2. Identify implicit assumptions and convert them into explicit rules.
3. Define strict boundaries for what is out of scope.

### Step 3: Technical Blueprint
Translate requirements into an architectural implementation plan:
1. File topology: Map modified and newly created files.
2. Component interfaces: Signatures, data classes, and schemas.
3. Deterministic tool mapping: Specify the exact Python scripts or MCP tools used.

### Step 4: Atomic Task Breakdown
Break the blueprint into small, ordered, verifiable milestones:
1. Order tasks by dependency sequence (dependencies first).
2. Attach an explicit test command to each milestone.
3. Provide a checkbox list for real time progress tracking.
