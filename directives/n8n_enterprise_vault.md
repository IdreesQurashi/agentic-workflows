# n8n Enterprise Workflow Integration Directive

## 1. Directive Scope & Objective
Govern production grade low code and agentic hybrid workflows connecting n8n webhooks, vector databases, CRM sync nodes, and external LLM APIs.

## 2. Core Execution Invariants
* Deterministic Webhook Handshake: Validate incoming webhook authentication tokens and request signatures before queuing execution payloads.
* Resumable Execution State: Store node execution checkpoints in external storage to guarantee idempotency across network retries.
* Structured Error Gating: Route failed node executions to dead letter queues with detailed error stack dumps and automated alert notifications.
* Zero Plaintext Credentials: All API credentials and OAuth secrets must reside in encrypted credential stores or secure environment variables.
