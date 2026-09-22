---
name: evaluator_critic
description: Conducts adversarial code evaluation, security auditing, and rubric scoring across security, correctness, performance, error handling, and maintainability.
---

# Evaluator Critic Skill

Use this skill when auditing pull request diffs, reviewing critical implementation code, or validating generated architecture plans against rigorous engineering criteria.

## When to Activate
* Prior to committing or merging critical code changes.
* When evaluating security boundaries, credentials, or API integrations.
* As the second loop in an Evaluator Optimizer pair.

## Evaluation Checklist and Rubric

### 1. Security & Safety (20 Points)
* Zero SQL injection, cross site scripting, or server side request forgery.
* Zero hardcoded credentials, API keys, or leaked sensitive variables.
* Strict input validation, path sanitization, and safe deserialization.

### 2. Functional Correctness (20 Points)
* Fulfills all functional requirements specified in the blueprint.
* Handles boundary conditions, null inputs, and unexpected types cleanly.
* Zero logic errors or off by one indexing mistakes.

### 3. Performance & Efficiency (20 Points)
* Avoids quadratic or exponential loops over unbounded datasets.
* Minimizes external API calls and database round trips.
* Respects memory limits and cleans up large buffers.

### 4. Robustness & Error Handling (20 Points)
* Explicit exception handling rather than blanket pass blocks.
* Graceful degradation and descriptive error telemetry.
* Safe cleanup in finally blocks or context managers.

### 5. Code Quality & Maintainability (20 Points)
* Clean variable and function names describing clear intent.
* Strict adherence to DRY and modular separation of concerns.
* Explicit type hints and docstrings.

## Output Format
Every review conducted with this skill must produce this standardized evaluation block:

```markdown
### Evaluator Assessment Report
* Total Score: [Score] / 100
* Verdict: [PASS / REVISE] (Threshold: 90 / 100)

### Critical Deficiencies (Must Address Before Merge)
* [file:line]: Description of vulnerability or fatal flaw.

### Optimization Notes and Suggestions
* [file:line]: Recommended refinement for readability or efficiency.
```
