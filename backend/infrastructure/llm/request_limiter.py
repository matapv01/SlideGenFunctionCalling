"""Process-wide concurrency gate for requests sent to one LLM endpoint."""

from __future__ import annotations

import threading
from contextlib import contextmanager
from typing import Iterator


class LLMRequestLimiter:
    """Bound concurrent model requests without changing workflow parallelism.

    Slide workers may still run in parallel, but all synchronous calls that use
    the shared Qwen endpoint pass through this gate.  This keeps the endpoint
    from receiving an unbounded mix of planner, generator, and VLM requests.
    """

    def __init__(self, max_concurrency: int = 5) -> None:
        self.max_concurrency = max(1, int(max_concurrency))
        self._semaphore = threading.BoundedSemaphore(self.max_concurrency)

    @contextmanager
    def slot(self) -> Iterator[None]:
        self._semaphore.acquire()
        try:
            yield
        finally:
            self._semaphore.release()
