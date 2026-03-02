from __future__ import annotations

from collections import defaultdict
from threading import Lock


class InMemoryMetrics:
    def __init__(self) -> None:
        self._lock = Lock()
        self._count_by_key: dict[str, int] = defaultdict(int)
        self._latency_sum_ms: dict[str, float] = defaultdict(float)

    def observe_request(self, method: str, path: str, status: int, latency_ms: float, case: str) -> None:
        key = self._key(method, path, status, case)
        with self._lock:
            self._count_by_key[key] += 1
            self._latency_sum_ms[key] += latency_ms

    def snapshot(self) -> dict[str, list[dict[str, float | int | str]]]:
        with self._lock:
            rows = []
            for key, count in self._count_by_key.items():
                method, path, status, case = key.split('|')
                latency_sum = self._latency_sum_ms[key]
                rows.append(
                    {
                        'method': method,
                        'path': path,
                        'status': int(status),
                        'caso_de_uso': case,
                        'count': count,
                        'avg_latency_ms': round(latency_sum / max(count, 1), 2),
                    }
                )
        rows.sort(key=lambda row: (row['path'], row['method'], row['status'], row['caso_de_uso']))
        return {'requests': rows}

    @staticmethod
    def _key(method: str, path: str, status: int, case: str) -> str:
        return f'{method}|{path}|{status}|{case}'
