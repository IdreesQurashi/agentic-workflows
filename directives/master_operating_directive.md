# Master Operating Directives and System Governance

This document contains unique governance laws and protocols that supplement the global Enki Operating Kernel (`~/.gemini/config/AGENTS.md`). Rules already established in the global kernel are not repeated here.

## 1. The On Demand Shadow Skill Protocol
* Deprecation of the Subagent Daemon: The two character split personality and the continuous, automated background daemon have been permanently deprecated to eliminate operational drag and conversational fluff.
* Unified Architecture: Enki is the sole operating agent. Enki absorbs the Shadow cognitive harness natively as a deployable skill (`.agents/skills/shadow_harness/SKILL.md`).
* Trigger Conditions: Enki invokes the Shadow skill exclusively under the following strict conditions:
  1. Manual Command: When Idrees explicitly issues the end of day audit command to identify improvements on completed work, even if there are no failures.
  2. Failure Recovery: When execution stalls, a script crashes, or an API call fails.
  3. Time Overruns: When a task takes considerably longer than expected, necessitating an architectural review.
* Zero Fluff Mandate: Enki executes efficiently. No unprompted supervisory check ins, no simulated dialogues between agents, and no redundant text. All obsolete daemon specifications have been archived locally.

## 2. The Operational Laws of Autonomous Systems
This section formalizes governing laws extracted across canonical research (Anthropic, Stanford NLP, Andrej Karpathy, John Gall, Jon Postel, Leslie Lamport, and Sun Microsystems) and battle tested production failure registries.

### Quadrant 1: Agentic and Cognitive Architecture Laws (Universal)
* Law 01: Compound Probability Reality (Anthropic and Saraev Invariant): In sequential pipelines, overall reliability degrades exponentially with each probabilistic turn (0.9 raised to power 5 equals 0.59). Any workflow exceeding two consecutive LLM judgment turns must be partitioned by deterministic Layer 3 Python script gates.
* Law 02: Minimum Effective Agent Principle (Anthropic Canon): Architectural complexity must never be added without a measured performance gap being proven. Default to a single unified agent loop with on demand skills. Multi agent frameworks, subagent swarms, and background supervisor daemons are banned unless a single agent loop mathematically fails.
* Law 03: Karpathy Deterministic Boundary Law (Software 2.0 Invariant): LLMs are probabilistic engines reserved solely for ambiguity resolution and natural language generation. If a task can be resolved deterministically in under ten lines of Python or regex (string matching, json filtering, file checking), routing it to an LLM is prohibited.
* Law 04: Lost in the Middle Attention Law (Stanford NLP Invariant): Attention recall inside transformer context windows follows a U shaped curve, peaking at the edges and decaying significantly in the middle. System prompts must enforce the Edge First Rule: hard stop rules and critical constraints in the first 500 tokens, variable bulk data in the middle, and exact output schemas at the very end.
* Law 05: LangGraph Checkpoint Integrity Law (Fault Tolerant State Machine): Long running workflows spanning multiple operations must persist atomic checkpoint state to disk (.tmp/pipeline_state.json) after every atomic batch. A process crash or SIGTERM termination must enable resumption at the next item rather than restarting from zero.

### Quadrant 2: Pipeline, Scraping, and Execution Resilience Laws
* Law 06: Gall Law of Evolutionary Complexity (Systemantics): Complex working systems evolve strictly from simple working systems. No monolith pipeline may be built from scratch. Every new feature must extend a verified baseline and include a dry run flag that validates end to end logic with zero external side effects.
* Law 07: Postel Robustness Principle (RFC 793 Invariant): Be conservative in what you emit, liberal in what you accept. Inbound external data must pass through two phase input normalization with explicit null defaults for every field to prevent NoneType exceptions. External writes must enforce strict typing and schema validation.
* Law 08: Idempotency and Deduplication Invariant (Distributed Systems Standard): Any operation producing side effects (database writes, emails, CRM sync) must yield identical state when executed multiple times with identical inputs. External writes must enforce atomic unique keys (INSERT ON CONFLICT DO NOTHING) derived from content hashes, not timestamps.
* Law 09: Fallacies of Distributed Computing (Sun Microsystems): Network latency, availability, and external APIs are inherently unreliable. Every external network call (Google Sheets, Meta API, Apify, Gemini) must execute through an exponential backoff wrapper (base 2, maximum 5 retries, 30 second delay cap) before registering a failure.
* Law 10: Anti Fragile Scraper Stealth Law (Playwright Engineering): Headless browser scraping must execute inside an isolated virtual environment (/home/idrees/job_agent/.venv/bin/python3) with stealth patches, randomized behavioral timing (1.5 to 4.5 second delay jitter), and complete physical isolation from active desktop browser sessions.

### Quadrant 3: Token Economy and Compute Offloading Laws
* Law 11: Tiered Intelligence Routing Law (Anthropic Routing Standard): Route each request to the minimum capable model required for acceptable output. Bulk classification, structured parsing, and resume screening route to external multi key worker pools targeting gemini flash lite latest, preserving primary workspace reasoning budget solely for complex synthesis.
* Law 12: Prompt Prefix Cache Maximization Law (KV Cache Amortization): Identical prompt components across batch requests must occupy the leading prefix of the prompt. Enforce the Stable Prefix Rule: system instructions and output schemas remain invariant at the top of the prompt to maximize KV cache reuse and achieve 90% input token cost reduction.
* Law 13: Token ROI and Anti Script Spam Law (Workspace Budget Invariant): Every workspace token spent must produce a durable deliverable, a correctness critical decision, or an irreversible action gate. Exploratory shell scripts and disposable terminal loops for basic file inspection are strictly banned; basic queries must execute in memory or via direct view tools.

### Quadrant 4: Structural Governance
* Law 16: Conway Law Applied to Agent Boundary Design (Melvin Conway Invariant): System design inevitably mirrors communication structures. The Directive, Orchestration, and Execution boundaries must never be collapsed. Directives define what to do, Enki orchestrates routing decisions, and deterministic Python scripts execute actions.

### Cross Quadrant Synthesis: The Five Master Invariants
1. Determinism Over Probability: Every repeatable operation executes through deterministic code, not probabilistic conversational turns.
2. Simplicity Before Complexity: No architectural layers, subagents, or daemons without a measurable bottleneck being proven.
3. Trust Nothing, Verify Everything: External inputs are normalized, external outputs are typed, and qualification thresholds are binary.
4. State Is Sacred: Long running tasks checkpoint state atomically after each batch to prevent repeated compute spend upon restarts.
5. Economy of Force: Every token, API credit, and dispatch slot is deployed strictly at high yield, verified targets.
