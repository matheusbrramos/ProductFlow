from __future__ import annotations

import time
from typing import Callable, TypeVar

T = TypeVar("T")


def retry_call(
    fn: Callable[[], T],
    *,
    retries: int = 3,
    base_delay_seconds: float = 1.0,
    retryable: Callable[[Exception], bool] | None = None,
) -> T:
    attempt = 0
    while True:
        try:
            return fn()
        except Exception as exc:  # noqa: BLE001
            attempt += 1
            should_retry = attempt <= retries and (retryable(exc) if retryable else True)
            if not should_retry:
                raise
            delay = base_delay_seconds * (2 ** (attempt - 1))
            time.sleep(delay)

