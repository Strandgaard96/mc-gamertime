import importlib


def _route_paths(app) -> list[str]:
    return [route.path for route in app.routes]


def test_metrics_route_not_registered_by_default(monkeypatch):
    monkeypatch.delenv("METRICS_ENABLED", raising=False)
    import main

    importlib.reload(main)
    try:
        assert "/metrics" not in _route_paths(main.app)
    finally:
        importlib.reload(main)


def test_metrics_route_registered_when_enabled(monkeypatch):
    monkeypatch.setenv("METRICS_ENABLED", "true")
    import main

    importlib.reload(main)
    try:
        assert "/metrics" in _route_paths(main.app)
    finally:
        monkeypatch.delenv("METRICS_ENABLED", raising=False)
        importlib.reload(main)


def test_metrics_endpoint_returns_prometheus_text(monkeypatch):
    from fastapi.testclient import TestClient

    monkeypatch.setenv("METRICS_ENABLED", "true")
    import main

    importlib.reload(main)
    try:
        monkeypatch.setattr(main, "_origin_token", "test-origin-token")
        monkeypatch.setattr(main, "_initialized", True)
        c = TestClient(main.app, raise_server_exceptions=False)

        resp = c.get("/api/health", headers={"x-origin-token": "test-origin-token"})
        assert resp.status_code == 200

        metrics_resp = c.get("/metrics", headers={"x-origin-token": "test-origin-token"})
        assert metrics_resp.status_code == 200
        assert "http_requests_total" in metrics_resp.text
        assert 'path="/api/health"' in metrics_resp.text
    finally:
        monkeypatch.delenv("METRICS_ENABLED", raising=False)
        importlib.reload(main)
