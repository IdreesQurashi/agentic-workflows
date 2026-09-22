---
name: context_optimizer
description: Enforces context window hygiene, progressive disclosure, token economy management, and offloading heavy batch workloads to external worker pools.
---

# Context Optimizer Skill

Use this skill to protect context window limits, reduce token consumption, and eliminate performance degradation across extended coding sessions.

## When to Activate
* Session history approaches or exceeds 20 conversation turns.
* Planning large batch data processing, web scraping audits, or bulk evaluations.
* Prior to dispatching multi agent operations or large scale research tasks.

## Core Rules

### 1. In Memory Analytical Standard
Simple reasoning tasks, JSON structure checks, and file reading must execute in memory within seconds. Never write or run throwaway terminal scripts for trivial checks.

### 2. External Pool Offloading
Batch text evaluations, bulk lead scrubbing, and high volume scraping audits must be offloaded to the external 6 key Gemini rotating pool (`gemini_worker.py`), preserving zero Antigravity workspace tokens.

### 3. Model Target Calibration
Always target `gemini-flash-lite-latest` for rotating worker pools. Avoid `gemini-flash-latest` which targets 3.8 flash and exhausts its 20 request daily free limit rapidly.

## Procedure

### Step 1: Context Audit
1. Review current context usage and turn depth.
2. Identify whether intermediate data or large terminal dumps are lingering in conversation memory.

### Step 2: Intermediate Data Eviction
1. Flush raw HTML, CSV, or scraping logs out of the prompt context.
2. Save raw outputs into `.tmp/` and maintain only concise file paths or schema summaries in working memory.

### Step 3: Trigger Compaction
When context saturation begins to impact prompt response speed or reasoning clarity:
1. Summarize completed project milestones.
2. Retain only active constraints, unresolved questions, and the immediate next task.
3. Clean out redundant conversational exchanges.
