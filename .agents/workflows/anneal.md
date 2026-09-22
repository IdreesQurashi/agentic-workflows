# Self Annealing Antigravity Workflow

Execute the Self Annealing failure recovery and system hardening workflow for the most recent crash or specified error: $ARGUMENTS.

## Execution Instructions
1. Load and activate the `self_annealer` skill.
2. Read `directives/workflows/06_self_annealing_failure_recovery.md` for complete SOP governance.
3. Parse the failure vector from stderr, terminal output, or execution logs.
4. Construct a standalone minimal reproducer script at `.tmp/reproduce_error.py`.
5. Execute the reproducer to confirm the failure state.
6. Apply the deterministic patch to the underlying script in `execution/` or environment configuration.
7. Verify that the reproducer and the wider test suite now execute with exit code 0.
8. Update the relevant SOP in `directives/` and record the root cause and resolution in the Failure Registry.
