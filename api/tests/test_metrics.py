from prometheus_client import REGISTRY

from lib.metrics import record_request


def _sample_value(name: str, labels: dict) -> float | None:
    for metric in REGISTRY.collect():
        for sample in metric.samples:
            if sample.name == name and sample.labels == labels:
                return sample.value
    return None


def test_record_request_increments_counter():
    before = (
        _sample_value(
            "http_requests_total", {"method": "GET", "path": "/api/health", "status": "200"}
        )
        or 0
    )
    record_request("GET", "/api/health", 200, 0.01)
    after = _sample_value(
        "http_requests_total", {"method": "GET", "path": "/api/health", "status": "200"}
    )
    assert after == before + 1


def test_record_request_observes_latency():
    record_request("GET", "/api/health", 200, 0.05)
    bucket_value = _sample_value(
        "http_request_duration_seconds_count", {"method": "GET", "path": "/api/health"}
    )
    assert bucket_value is not None and bucket_value >= 1
