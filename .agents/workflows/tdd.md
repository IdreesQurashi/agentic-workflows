# Test Driven Development Antigravity Workflow

Execute the Test Driven Development workflow for the specified implementation plan or target module: $ARGUMENTS.

## Execution Instructions
1. Load and activate the `tdd_engine` skill.
2. Read `directives/workflows/03_tdd_and_verification_engine.md` for complete SOP governance.
3. Detect the active test runner in the workspace (pytest, unittest, vitest, bun test).
4. For each required capability, execute the RED phase: author tests asserting required behavior and verify failure with recorded log.
5. Execute the GREEN phase: implement minimal code to satisfy assertions and verify exit code 0.
6. Execute the REFACTOR phase: clean and optimize while maintaining passing tests.
7. Verify at least 80% test coverage and document all verification evidence.
