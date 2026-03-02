from __future__ import annotations

import time
from collections import defaultdict, deque
from threading import Lock


class InMemoryAdminRateLimiter:
    def __init__(self, max_requests: int = 60, window_seconds: int = 60) -> None:
        self.max_requests = max_requests
        self.window_seconds = window_seconds
        self._lock = Lock()
        self._requests: dict[str, deque[float]] = defaultdict(deque)

    def allow(self, client_key: str) -> bool:
        now = time.time()
        lower_bound = now - self.window_seconds
        with self._lock:
            bucket = self._requests[client_key]
            while bucket and bucket[0] < lower_bound:
                bucket.popleft()
            if len(bucket) >= self.max_requests:
                return False
            bucket.append(now)
            return True

    def reset(self) -> None:
        with self._lock:
            self._requests.clear()
