from fastapi.testclient import TestClient

from main import app


def test_origin_guard_disabled_allows_without_token(monkeypatch):
    monkeypatch.setenv("ORIGIN_GUARD_ENABLED", "false")
    c = TestClient(app, raise_server_exceptions=False)
    resp = c.get("/api/health")
    assert resp.status_code == 200


def test_origin_guard_off_by_default(monkeypatch):
    # The guard only makes sense behind CloudFront, so selfhost — the default
    # deployment — must not need to switch it off. The cloud path opts in via
    # ORIGIN_GUARD_ENABLED=true in infra/lambda.tf.
    monkeypatch.delenv("ORIGIN_GUARD_ENABLED", raising=False)
    c = TestClient(app, raise_server_exceptions=False)
    resp = c.get("/api/health")
    assert resp.status_code == 200


def test_origin_guard_enabled_blocks_without_token(monkeypatch):
    monkeypatch.setenv("ORIGIN_GUARD_ENABLED", "true")
    c = TestClient(app, raise_server_exceptions=False)
    resp = c.get("/api/health")
    assert resp.status_code == 403
