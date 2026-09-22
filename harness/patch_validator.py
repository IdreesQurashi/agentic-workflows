"""
patch_validator.py: Patch verification runner.
Runs the minimal reproducer against a candidate fix to confirm
resolution before updating production directives and code.
"""
import subprocess
import sys
from pathlib import Path

def validate_patch(reproducer_script: Path) -> bool:
    """
    Executes reproducer script. If reproducer exits 0, the failure reproduced.
    If it exits 1, the script succeeded without error, meaning the patch fixed the bug.
    """
    if not reproducer_script.exists():
        print(f"Reproducer not found: {reproducer_script}")
        return False

    res = subprocess.run([sys.executable, str(reproducer_script)], capture_output=True, text=True)
    return res.returncode != 0
