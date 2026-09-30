from __future__ import annotations

import time
from concurrent.futures import ThreadPoolExecutor, TimeoutError as FutTimeout
from typing import Callable, TypeVar

T = TypeVar("T")


class RetryExhausted(RuntimeError):
    def __init__(self, attempts: int, last_error: Exception):
        super().__init__(f"failed after {attempts} attempts: {last_error!r}")
        self.attempts, self.last_error = attempts, last_error


def call_with_retry(fn: Callable[[], T], attempts: int = 2, timeout_s: float = 8.0, backoff_s: float = 0.2,
                    validate: Callable[[T], None] | None = None) -> T:
    """Run fn with a timeout, bounded retries and optional output validation.
    Raises RetryExhausted (never loops forever). Timed-out worker threads are abandoned, not killed."""
    last: Exception = RuntimeError("no attempt made")
    for i in range(max(1, attempts)):
        ex = ThreadPoolExecutor(max_workers=1)
        try:
            fut = ex.submit(fn)
            out = fut.result(timeout=timeout_s)
            if validate:
                validate(out)
            return out
        except FutTimeout as e:
            last = TimeoutError(f"timeout after {timeout_s}s")
            last.__cause__ = e
        except Exception as e:  # noqa: BLE001 - we deliberately convert everything to retry/exhaust
            last = e
        finally:
            ex.shutdown(wait=False, cancel_futures=True)
        if i < attempts - 1:
            time.sleep(backoff_s * (i + 1))
    raise RetryExhausted(max(1, attempts), last)
