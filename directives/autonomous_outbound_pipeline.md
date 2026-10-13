# Autonomous Outbound Intelligence and Deliverability Directive

## 1. Directive Scope and Objective
Define standard operating procedures for autonomous B2B lead intelligence, candidate qualification, and outbound dispatch. Operational invariants (verbal order gate, two strike breaker) are enforced by the global Enki kernel and not repeated here.

## 2. Data Flow Architecture
1. Extraction: Headless Playwright script navigates employer ATS pages (Ashby, Greenhouse, Lever, Workable).
2. Evaluation: Batch profiles offloaded to external Gemini Flash Lite workers for rubric scoring against core tech stacks.
3. Verification: DNS MX records checked deterministically before staging any email address.
4. Dispatch: Paced background daemon consumes the verified queue with randomized sleep intervals (900 to 1800 seconds between sends).

## 3. Deliverability Invariants
* Deliverability Bounce Floor: Target hard bounce rate must remain below 0.25%. A single bounce triggers an immediate 12 to 24 hour sending cooldown on the sender domain and permanently blacklists the target address.
