# Headless Goal Runner Slash Command

Execute autonomous, long running goal pursuit for the specified objective: $ARGUMENTS.

## Execution Instructions
1. Read `directives/workflows/08_headless_goal_and_ci_runner.md` for complete SOP governance.
2. Establish the binary completion contract: list all verifiable deliverables, file creations, and passing test commands required.
3. Initialize the resumable state registry at `.tmp/goal_state.json`.
4. Deconstruct the objective into atomic milestones.
5. For each milestone, execute required deterministic tools, verify outcomes against tests, and record checkpoints.
6. If an execution failure occurs, invoke the `self_annealer` skill to diagnose, patch, and recover.
7. Terminate and emit the completion marker only when every single item in the binary completion contract is empirically verified with exit code 0.
