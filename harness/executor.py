"""
executor.py: Deterministic execution wrapper and worker router.
Runs tasks with error isolation, automated crash capture, and external
Gemini worker pool routing for bulk analytical workloads.
"""
import os
import subprocess
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import List, Optional

HARNESS_DIR = Path(__file__).resolve().parent
ROOT_DIR = HARNESS_DIR.parent

sys.path.insert(0, str(HARNESS_DIR))
from crash_capture import capture_crash
from fixture_author import author_reproducer

WORKER_POOL_THRESHOLD = 10
WORKER_MODEL = "gemini-flash-lite-latest"

def should_route_to_worker_pool(task_count: int) -> bool:
    """Route to external Gemini pool when batch size exceeds threshold."""
    return task_count > WORKER_POOL_THRESHOLD

@dataclass
class ExecutionResult:
    success: bool
    returncode: int
    stdout: str
    stderr: str
    crash_record: Optional[dict] = None
    reproducer_path: Optional[Path] = None

def run_script(script_path: str, args: Optional[List[str]] = None, env: Optional[dict] = None) -> ExecutionResult:
    """
    Executes a script with subprocess isolation and automatic crash capture.
    """
    args = args or []
    full_env = os.environ.copy()
    if env:
        full_env.update(env)

    cmd = [sys.executable, str(script_path)] + args
    res = subprocess.run(cmd, capture_output=True, text=True, env=full_env)

    if res.returncode != 0:
        crash_record = capture_crash(
            script_path=script_path,
            args=args,
            exit_code=res.returncode,
            stderr=res.stderr,
            stdout=res.stdout
        )
        reproducer_path = author_reproducer(crash_record)
        return ExecutionResult(
            success=False,
            returncode=res.returncode,
            stdout=res.stdout,
            stderr=res.stderr,
            crash_record=crash_record,
            reproducer_path=reproducer_path
        )

    return ExecutionResult(
        success=True,
        returncode=0,
        stdout=res.stdout,
        stderr=res.stderr
    )
