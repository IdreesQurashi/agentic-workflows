# Evaluator Review Slash Command

Execute the Evaluator Critic adversarial code and security review for the current workspace or specified files: $ARGUMENTS.

## Execution Instructions
1. Load and activate the `evaluator_critic` skill.
2. Read `directives/workflows/05_evaluator_optimizer_loop.md` for complete SOP governance.
3. Extract git diff of modified files or inspect specified target components.
4. Score candidate changes across the five rubric dimensions:
   * Security and Safety (20 points)
   * Functional Correctness (20 points)
   * Performance and Efficiency (20 points)
   * Robustness and Error Handling (20 points)
   * Maintainability and Code Cleanliness (20 points)
5. Emit standardized assessment report with total score out of 100 and explicit PASS or REVISE verdict.
6. List all critical deficiencies requiring remediation before merge.
