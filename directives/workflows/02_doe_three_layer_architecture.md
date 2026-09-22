# Directive: The Three Layer Architecture Workflow (DOE)

## 1. Executive Summary
The Three Layer Architecture is the foundational operational standard designed to bridge the mismatch between probabilistic LLM reasoning and deterministic software execution. LLMs are probabilistic, whereas business operations and data pipelines demand consistency. By strictly dividing responsibilities into Directive, Orchestration, and Execution, this workflow prevents compounding errors and ensures bulletproof reliability.

```mermaid
flowchart TD
    subgraph Layer 1: Directive
        D[Standard Operating Procedures in Markdown]
        G[Goals, Inputs, Constraints, Edge Cases]
    end

    subgraph Layer 2: Orchestration
        O[Intelligent Agent Decision Router]
        R[Task Planning, Error Handling, Context Curation]
    end

    subgraph Layer 3: Execution
        E[Deterministic Python Scripts and Tools]
        T[APIs, File Operations, Database Mutations]
    end

    Layer 1 --> Layer 2
    Layer 2 --> Layer 3
    Layer 3 -- Results and Telemetry --> Layer 2
    Layer 2 -- System Annealing and SOP Updates --> Layer 1
```

---

## 2. Mathematical Rationale: Compounding Accuracy
When an autonomous agent attempts to execute multi step business logic manually using raw text prediction:
* A 90% accuracy rate across 5 consecutive probabilistic decisions yields a combined success rate of only 59%.
* Across 10 consecutive decisions, the success rate plummets to 34%.
* Solution: Delegate sequential complexity to deterministic Python scripts (Layer 3). When deterministic tools have 99.9% reliability, the agent (Layer 2) focuses purely on routing and exception handling, maintaining high end to end fidelity.

---

## 3. The Three Layers

### Layer 1: Directive (What to Do)
* Format: Standard Operating Procedures (SOPs) written in Markdown, stored in `directives/`.
* Responsibility: Defines business goals, required inputs, deterministic tools to invoke, expected deliverables, and known edge cases.
* Persona: Written with the clarity of instructions provided to a high performing senior engineer.
* Lifecycle: Living documents that are continuously updated through the self annealing loop.

### Layer 2: Orchestration (Decision Making)
* Format: The reasoning AI model operating in session memory (Enki).
* Responsibility: Reads the Directive, inspects inputs, validates preconditions, invokes execution tools in the correct order, analyzes return codes, and handles errors.
* Boundary: Never performs complex mathematical calculations, large scale text scraping, or raw API calls directly in the prompt context. Always routes execution to Layer 3 tools.

### Layer 3: Execution (Doing the Work)
* Format: Deterministic Python scripts stored in `execution/` or external MCP tools.
* Environment: Isolated virtual environment with strict dependency management and environment variable bindings (`.env`).
* Responsibility: Executes external API calls, database operations, file transformations, and network requests.
* Guarantees: Fast, unit tested, idempotent, and produces structured outputs (JSON, CSV) and explicit exit codes.

---

## 4. File Organization and Separation of Concerns

| Directory | Layer | Purpose | Persistence Rule |
| :--- | :--- | :--- | :--- |
| `directives/` | Layer 1 | System SOPs and operational directives | Permanent, tracked in version control |
| `execution/` | Layer 3 | Deterministic scripts and tooling | Permanent, tracked in version control |
| `.tmp/` | Scratch | Intermediate data, scraped cache, temp payloads | Ephemeral, safe to purge at any time |
| Deliverables | Cloud / External | Production sheets, databases, client reports | Master output destinations |

---

## 5. Execution Rules and Self Annealing Loop
1. Tool Discovery First: Before writing a new script or modifying existing files, inspect `execution/` to determine if a deterministic tool already exists.
2. Script Overwrite Protection: Never overwrite an existing execution script without verifying backward compatibility.
3. Closed Loop Recovery: When a Layer 3 script fails, the Layer 2 orchestrator parses stderr, patches the script, verifies against tests, and updates the Layer 1 directive with the new edge case insight.
