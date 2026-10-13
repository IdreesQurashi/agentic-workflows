# Core Engineering: State Ledger

## Last Updated
2026-10-03 21:14 PKT

## LiteLLM Proxy and Claude Code Bridge
* Configuration File: /home/idrees/litellm_config.yaml (symlinked from /home/idrees/Antigravity/claude_proxy/litellm_config.yaml).
* Working Directory: /home/idrees/Antigravity/claude_code/.
* Model Routing: Routes claude-opus-5, claude-sonnet-5, claude-haiku-4-5, claude-3-7-sonnet, claude-3-5-sonnet across rotating keys targeting gemini/gemini-flash-lite-latest.
* Router Settings: Strategy is simple-shuffle, 3 retries, cooldown 30 seconds, retry delay 1 second.
* Status: Configured and active.

## Gemini 6 Key Rotating Worker Pool
* Pool Configuration: /home/idrees/Antigravity/job_agent/gemini_keys_pool.json.
* Execution Script: gemini_worker.py.
* Model Target: Strictly gemini-flash-lite-latest (protects free tier quota and eliminates 429 exhaustion).
* Purpose: Offload batch text processing, resume evaluations, and scraping audits from workspace context.

## n8n Local Instance
* Installation Directory: /home/idrees/Antigravity/n8n-local/.
* Migration Status: 27 versions behind (identified during Project I4 update readiness pack).
* Update Pack Assets: Automated backup workflows and pre migration verification SOPs generated in legacy_archive/directives/.
* Execution Standard: n8n is strictly an orchestration layer. Complex logic, Playwright loops, and scraping must execute via deterministic Python backend.

## Playwright Dedicated Virtual Environment
* Path: /home/idrees/job_agent/.venv/bin/python3.
* Invariant: All browser automation and scraping scripts execute inside this isolated environment. Attaching to personal desktop Chrome is strictly prohibited.

## Security Tooling and Penetration Testing
* Tool: Burp Suite Pro removed to reclaim local storage. Installer script purged.

## Connected MCP Mesh (12 Active Servers)
* Configuration: /home/idrees/Antigravity/Agentic Workflows-20260907T212811Z-1-001/Agentic Workflows/.mcp.json.
* Active Servers: job_hunter_engine, lead_engine, gmail_engine, google_workspace, memory_graph, notifier, pc_master, media_studio, daily_agenda, github_engine, live_search, claude_code_engine.

## E Paper Standalone Autopublisher
* Path: execution/epaper_autopublisher/.
* Status: Production active. Replaced Make.com cloud scenarios to bypass 512 MB data limit.
* Ingestion: Direct IMAP via Gmail App Password.
* Publishing: Native WordPress REST API using iwc-api-key authentication with DearFlip flipbook embed.
* Supported Publications: Daily Pukkar e Azadi (4 pages) and Daily Kashmir Times (8 pages).
* Idempotency: Multi-batch aggregation and natural deduplication prevents duplicate pages and split posts.

## In Flight and Blockers
* Plan safe upgrade path for local n8n instance from 27 versions behind without breaking custom nodes.

## Remaining Work (Pick up here)
* Add 02:00 AM cron entry for epaper_autopublisher if automated schedule is desired.
* Run backup workflow on local n8n workflows before triggering version bump.
* Test LiteLLM proxy latency under multi key shuffle.
