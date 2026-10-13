---
name: core_engineering
description: Execution protocol for local infrastructure management including n8n orchestration, Gemini worker pools, proxy routing, and security tooling.
---

# Core Engineering Execution Protocol

This skill governs the maintenance and development of Idrees's local infrastructure stack. Activate when working on n8n workflows, Gemini pool operations, proxy configurations, or security tooling.

## 1. n8n Local Orchestration
* n8n is strictly an Orchestration Layer. Never build complex logic, heavy data transformation, or web scraping loops directly in n8n nodes.
* Route complex processing to the deterministic Python backend (`/home/idrees/job_agent/.venv/bin/python3`) via HTTP Requests.
* Use n8n exclusively for its native strengths: Webhooks, HTTP Requests, Switch/If logic, and Google Sheets integration.
* For detailed error handling architecture, node management, and troubleshooting, consult the `n8n_mastery` skill.

## 2. Gemini 6 Key Worker Pool
* Pool Configuration: 6 API keys rotating via `gemini_worker.py` located at `/home/idrees/Antigravity/job_agent/gemini_keys_pool.json`.
* Model Target: Always `gemini-flash-lite-latest`. Never use the standard flash alias.
* Purpose: Offload batch text processing, bulk evaluations, lead scrubbing, and scraping audits from the Antigravity workspace to preserve primary reasoning budget.
* Health Monitoring: Verify key rotation is active and no single key has exhausted its quota before launching batch operations.

## 3. LiteLLM Proxy and Claude Code Bridge
* Config Location: `/home/idrees/litellm_config.yaml` (symlinked from `/home/idrees/Antigravity/claude_proxy/litellm_config.yaml`).
* Purpose: Routes Claude Code requests through LiteLLM proxy to enable model flexibility and key rotation.
* Claude Code Directory: `/home/idrees/Antigravity/claude_code/`.

## 4. Playwright Backend Isolation
* Virtual Environment: `/home/idrees/job_agent/.venv/bin/python3`.
* Invariant: All headless browser automation runs inside this dedicated venv. Never attach to the user personal desktop Chrome browser or manipulate graphical debug ports.
* Stealth Patches: Randomized behavioral timing (1.5 to 4.5 second delay jitter) and complete physical isolation from active desktop browser sessions.

## 5. Security Tooling
* Burp Suite Pro: Installed for web application security testing.
* Penetration testing assets stored in `/home/idrees/poc.burp`.

## 6. MCP Server Infrastructure
* Configuration: `.mcp.json` in workspace root.
* Active Servers: job_hunter_engine, lead_engine, gmail_engine, google_workspace, memory_graph, notifier, pc_master, media_studio, daily_agenda, github_engine, live_search, claude_code_engine.
* When adding or modifying MCP servers, always verify connection health after changes.
