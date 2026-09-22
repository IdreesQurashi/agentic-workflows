"""
directive_updater.py: Self annealing knowledge recorder.
Appends validated failure recovery notes to directives.
"""
from datetime import datetime, timezone
from pathlib import Path

HARNESS_DIR = Path(__file__).resolve().parent
ROOT_DIR = HARNESS_DIR.parent
DIRECTIVES_DIR = ROOT_DIR / "directives"

def record_learning(directive_name: str, issue_summary: str, root_cause: str, solution: str):
    """
    Appends a new self annealing failure entry to the specified directive.
    """
    target_directive = DIRECTIVES_DIR / directive_name
    if not target_directive.exists():
        target_directive = DIRECTIVES_DIR / "master_operating_directive.md"

    timestamp = datetime.now(timezone.utc).strftime("%Y.%m.%d")
    entry = f"""
### Failure Recovery Record ({timestamp})
* Issue: {issue_summary}
* Root Cause: {root_cause}
* Resolution: {solution}
"""
    with open(target_directive, "a", encoding="utf-8") as f:
        f.write(entry)
    print(f"Recorded learning to {target_directive.name}")
