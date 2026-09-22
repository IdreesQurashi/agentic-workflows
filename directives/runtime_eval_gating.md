# Runtime Evaluation Driven Development (EDD) Directive

## 1. Directive Scope & Objective
Establish runtime gating procedures using LLM as a Judge architectures to inspect, score, and validate agent outputs before triggering external actions.

## 2. Core Evaluation Invariants
* Deterministic Scoring Rubric: Evaluate candidates across relevance, factual grounding, and spam or hallucination triggers using normalized floating point metrics between 0.0 and 1.0.
* 85% Confidence Floor: Any generated outreach, summary, or transformed artifact scoring below a 0.85 composite threshold must be rejected or routed for manual review.
* Factual Grounding Strictness: If factual grounding drops below 0.90 against the source data, reject the item immediately regardless of stylistic quality.
* Structured Pydantic Output: Judges must return structured outputs conforming to rigid Pydantic schemas, eliminating freeform parsing ambiguities.

## 3. Evaluation Decision Matrix
* Composite Score Calculation: Composite = (0.4 * Relevance) + (0.4 * Factual Grounding) + (0.2 * (1.0 - Spam Trigger Score)).
* Decision Rules:
  * Composite >= 0.85 and Grounding >= 0.90: APPROVE.
  * Composite < 0.85 or Grounding < 0.90: REJECT.
  * Ambiguity or Missing Ground Truth: ESCALATE to human operator.
