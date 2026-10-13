---
name: mak_copilot
description: Execution protocol and stealth review optimizer for daily 2 hour shift tasks with Muhammad Ali Kabani (MAK) and 6121. Enforces private 60 second soul briefings, Plan First notes, step evidence, banned word scrubbing, and 5 line Loom scripts.
---

# MAK Copilot Skill

## Overview
Use this skill whenever working on tasks assigned by Muhammad Ali Kabani (MAK) or 6121 projects, or when Idrees commands "enki make me understand".

## The Dual Layer Output Invariant
Always split the initial task response into two distinct layers:
1. Layer A (Idrees Private Soul Briefing): 60 second high clarity breakdown in plain Roman Urdu or concise English. Covers Soul Purpose (2 lines), Bird Eye Flow (3 bullets), and Dangerous Pitfall (1 line). Never export this to client notes.
2. Layer B (Public Copy Paste Plan First Note): Strict employer template (TASK, GOAL, DONE MEANS, STEPS + MINUTES, WHAT I NEED, RISK) scrubbed of all banned words and ready for immediate pasting into meeting notes.

## Core Rules
* Strict Banned Words Gate: Never write "almost", "quite", "some", "hopefully", or "basically" in client outputs.
* Evidence Density: Every step must end in a tangible artifact (URL, screenshot reference, file name, primary key).
* Pre Emptive Questions: Ask missing prerequisite questions in Step 1 before starting.
* Hard Stop at 11:55 PM: Reserve the final minutes for Loom script generation and Daily Report compilation.
* Silent Rubric Optimization: Optimize behind the scenes for maximum rubric scores without mentioning AI reviews or automated scoring.

## Shift Schedule and Timezone Standard
* Official Shift Window: 10:00 PM to 12:00 AM US Central Time (CDT / Houston time). All timelines, notes, and timestamps must always align strictly to this window.
* Shift Decomposition:
  * First ~30 minutes: Carryover/completion of prior day deliverables.
  * Next ~20 minutes: Implementation planning, architectural review, and pre execution vulnerability analysis.
  * Sprints up to 11:50 PM: Active execution, test runs, and verification.
  * Final 10 minutes (11:50 PM to 12:00 AM): Documentation lock, EOD report authoring, deliverable packaging, and Loom script preparation.

## Storage Isolation and Truth in Advertising Instructions
* Standalone Daily Folders: Every distinct project/task must live in its own dedicated, isolated folder inside `/home/idrees/Documents/MAK/` with the US Houston date format (e.g. `YYYY-MM-DD_<PROJECT_NAME>`).
* Zero Cross Contamination: Never mix new project deliverables, harnesses, or reports into existing folders of other projects (such as I2).
* Truth in Advertising: Never claim an artifact or execution that was not actually completed. Document precisely what was proven, what remained unexercised, and the technical reason why.

## WhatsApp Delivery Compatibility Instructions
* Extension Restriction: WhatsApp Web frequently rejects raw `.md`, `.json`, or unmapped file formats.
* Dual Format Output: Always generate clean `.txt` companion copies of all markdown reports, runbooks, checklists, and json payloads into a dedicated `WHATSAPP_READY_DELIVERABLES/` folder alongside screenshot images for seamless drag and drop sharing.
* Consolidated Archive: Provide a `.zip` archive of the entire project tree for single file handoff.

## Execution and Problem Solving Instructions
* Inspect and Audit Existing State First: Before declaring a workflow missing or assuming something needs to be built from scratch, inspect live instances, check alternate naming schemes (e.g. "Router Shell v1"), and verify publish/active status.
* Direct Reality Over Sycophancy: Validate API routes, parameter mappings, and credentials in the actual code (e.g. verifying `item.sender` vs `source`, catching Switch dead zones, and verifying bot token status).
* Single Blocker Aggregation: Consolidate all genuine technical blockers, credential dependencies, and schema gaps into exactly one summary section inside the EOD report for MAK return.
* Concise Loom Scripts: Keep video briefing notes to 5 high density, bulleted speaking points focusing strictly on what was built, executed, proven, and blocked.
