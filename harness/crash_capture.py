"""
crash_capture.py: Runtime crash diagnostic and stack trace capture.
Parses stderr, captures exception traces, and logs structured crash records
to the append only failure registry.
"""
import json
import os
import sys
import traceback
from datetime import datetime, timezone
from pathlib import Path

HARNESS_DIR = Path(__file__).resolve().parent
ROOT_DIR = HARNESS_DIR.parent
REGISTRY_PATH = HARNESS_DIR / "failure_registry.jsonl"

def capture_crash(script_path: str, args: list, exit_code: int, stderr: str, stdout: str = "") -> dict:
    """
    Captures crash metadata and appends to failure_registry.jsonl.
    """
    lines = stderr.strip().splitlines()
    stderr_tail = "\n".join(lines[-10:]) if lines else ""
    
    exception_name = "UnknownError"
    for line in reversed(lines):
        if ":" in line and any(err in line for err in ["Error", "Exception", "Fault"]):
            exception_name = line.split(":")[0].strip()
            break

    crash_record = {
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "script": str(script_path),
        "args": [str(a) for a in args],
        "exit_code": exit_code,
        "exception_name": exception_name,
        "stderr_tail": stderr_tail,
        "stdout_tail": "\n".join(stdout.strip().splitlines()[-5:]) if stdout else "",
        "fixture_path": str(ROOT_DIR / ".tmp" / "reproduce_error.py"),
        "patch_applied": False,
        "resolved_at": None
    }

    try:
        with open(REGISTRY_PATH, "a", encoding="utf-8") as f:
            f.write(json.dumps(crash_record) + "\n")
    except Exception as e:
        print(f"Warning: Failed to write to failure registry: {e}", file=sys.stderr)

    return crash_record

def capture_current_exception(script_path: str = "") -> dict:
    """Captures currently unhandled exception via sys.exc_info."""
    exc_type, exc_val, exc_tb = sys.exc_info()
    formatted = "".join(traceback.format_exception(exc_type, exc_val, exc_tb))
    return capture_crash(
        script_path=script_path or sys.argv[0],
        args=sys.argv[1:],
        exit_code=1,
        stderr=formatted
    )
