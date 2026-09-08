"""Prometheus counters for the optional /metrics endpoint (METRICS_ENABLED=true).

Path labels use the route's templated path (e.g. /players/{id}), never the raw
URL, to keep cardinality bounded — see main.py's metrics_middleware.
"""

from __future__ import annotations

from prometheus_client import Counter, Histogram

REQUEST_COUNT = Counter("http_requests_total", "Total HTTP requests", ["method", "path", "status"])
REQUEST_LATENCY = Histogram(
    "http_request_duration_seconds", "HTTP request latency in seconds", ["method", "path"]
)


def record_request(method: str, path: str, status: int, duration_seconds: float) -> None:
    REQUEST_COUNT.labels(method=method, path=path, status=str(status)).inc()
    REQUEST_LATENCY.labels(method=method, path=path).observe(duration_seconds)
