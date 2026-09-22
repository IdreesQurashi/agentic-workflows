# Autonomous Outbound Intelligence & Deliverability Directive

## 1. Directive Scope & Objective
Define standard operating procedures for autonomous B2B lead intelligence, candidate qualification, and outbound dispatch under Zero Bounce OS principles.

## 2. Core Execution Invariants
* Zero Mailbox Guessing: Outbound messages may only target email addresses explicitly stated in official job listings or verified executive records. Never synthesize or extrapolate mailbox prefixes.
* Randomized Pacing Gate: Automated multi email loops must enforce randomized intervals between 900 and 1800 seconds between individual sends to protect sender reputation and avoid rate limiting flags.
* Deliverability Bounce Floor: Target hard bounce rate must remain below 0.25%. A single bounce triggers an immediate 12 to 24 hour sending cooldown on the sender domain and permanently blacklists the target address.
* External API Offloading: Bulk profile scoring and job description analysis must route to the rotating 6 key Gemini Flash Lite worker pool, consuming zero workspace context tokens.

## 3. Data Flow Architecture
1. Extraction: Headless Playwright script navigates employer ATS pages (Ashby, Greenhouse, Lever, Workable).
2. Evaluation: Batch profiles offloaded to external Gemini Flash Lite workers for rubric scoring against core tech stacks.
3. Verification: DNS MX records checked deterministically before staging any email address.
4. Dispatch: Paced background daemon consumes the verified queue with randomized sleep intervals.

## 4. Failure & Escalation Protocols
* Two Strike Task Breaker: If any scraping target or API fails twice consecutively, halt execution immediately and log the exact response trace.
* Human Verification Gate: Never trigger an external dispatch without explicit verbal review and confirmation from the human operator in chat.
