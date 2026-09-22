"""
_retry.py: Exponential backoff retry engine enforcing Law 09 (Fallacies of Distributed Computing).
Wraps network calls, API requests, and external writes with base 2 exponential backoff,
jitter, and strict logging.
"""
import time
import random
import sys
from typing import Callable, Any

def retry_with_backoff(
    func: Callable[[], Any],
    max_retries: int = 5,
    base_delay: float = 1.0,
    max_delay: float = 30.0,
    retryable_exceptions: tuple = (Exception,)
) -> Any:
    """
    Executes a callable with base 2 exponential backoff retry.
    """
    attempt = 0
    while True:
        try:
            return func()
        except retryable_exceptions as e:
            attempt += 1
            if attempt > max_retries:
                print(f"ERROR: Max retries ({max_retries}) exceeded. Failing operation: {e}", file=sys.stderr)
                raise e
            
            # Base 2 exponential backoff with full jitter
            calculated_delay = min(max_delay, base_delay * (2 ** (attempt - 1)))
            jittered_delay = random.uniform(calculated_delay * 0.5, calculated_delay * 1.5)
            
            print(f"WARN: Attempt {attempt} failed ({e}). Retrying in {jittered_delay:.2f}s...", file=sys.stderr)
            time.sleep(jittered_delay)
