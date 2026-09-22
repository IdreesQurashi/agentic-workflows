"""
Enki Agent Kernel (Layer 2 Orchestrator)
Enforces master execution invariants, loads directives, and dispatches to Layer 3 tools.
"""

from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Callable, Dict, List, Optional
import logging

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
logger = logging.getLogger("EnkiKernel")


@dataclass
class TaskResult:
    success: bool
    data: Any = None
    error: Optional[str] = None
    attempt_count: int = 1
    breaker_tripped: bool = False


class EnkiKernel:
    """
    Autonomous System Orchestrator.
    Manages directive retrieval, execution state, and Two Strike Task Breaker governance.
    """

    def __init__(self, directives_dir: Optional[Path] = None):
        self.root_dir = Path(__file__).resolve().parent.parent
        self.directives_dir = directives_dir or (self.root_dir / "directives")
        self.strike_registry: Dict[str, int] = {}
        self.directives_cache: Dict[str, str] = {}

    def load_directive(self, directive_name: str) -> str:
        """Loads natural language SOP directive from Layer 1."""
        if not directive_name.endswith(".md"):
            directive_name = f"{directive_name}.md"

        if directive_name in self.directives_cache:
            return self.directives_cache[directive_name]

        target_file = self.directives_dir / directive_name
        if not target_file.is_file():
            raise FileNotFoundError(f"Directive '{directive_name}' not found in {self.directives_dir}")

        content = target_file.read_text(encoding="utf-8")
        self.directives_cache[directive_name] = content
        logger.info(f"Loaded directive '{directive_name}' successfully.")
        return content

    def execute_with_two_strike_breaker(
        self,
        task_id: str,
        execution_fn: Callable[..., Any],
        *args: Any,
        **kwargs: Any,
    ) -> TaskResult:
        """
        Executes a deterministic Layer 3 function with strict Two Strike Task Breaker gating.
        If a task fails on two consecutive attempts, halts execution and surfaces error.
        """
        current_strikes = self.strike_registry.get(task_id, 0)
        if current_strikes >= 2:
            logger.error(f"Two Strike Task Breaker TRIPPED for task '{task_id}'. Halting execution.")
            return TaskResult(
                success=False,
                error=f"Task '{task_id}' halted by Two Strike Task Breaker after 2 consecutive failures.",
                attempt_count=current_strikes,
                breaker_tripped=True,
            )

        try:
            result = execution_fn(*args, **kwargs)
            self.strike_registry[task_id] = 0
            return TaskResult(success=True, data=result, attempt_count=current_strikes + 1)
        except Exception as exc:
            new_strikes = current_strikes + 1
            self.strike_registry[task_id] = new_strikes
            logger.warning(f"Task '{task_id}' failed attempt {new_strikes}. Error: {exc}")

            if new_strikes >= 2:
                logger.error(f"Two Strike threshold reached for task '{task_id}'. Escalating.")
                return TaskResult(
                    success=False,
                    error=f"Two Strike Task Breaker tripped on task '{task_id}': {str(exc)}",
                    attempt_count=new_strikes,
                    breaker_tripped=True,
                )

            return TaskResult(success=False, error=str(exc), attempt_count=new_strikes, breaker_tripped=False)

    def reset_breaker(self, task_id: str) -> None:
        """Resets the failure counter for a specific task."""
        self.strike_registry[task_id] = 0
        logger.info(f"Reset strike registry for task '{task_id}'.")
