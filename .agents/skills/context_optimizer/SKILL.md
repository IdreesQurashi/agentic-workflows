---
name: context_optimizer
description: Enforces context window hygiene, progressive disclosure, and token economy management for extended coding sessions.
---

# Context Optimizer Skill

Use this skill to protect context window limits, reduce token consumption, and eliminate performance degradation across extended coding sessions.

## When to Activate
* Session history approaches or exceeds 20 conversation turns.
* Planning large batch data processing, web scraping audits, or bulk evaluations.
* Prior to dispatching multi agent operations or large scale research tasks.

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
