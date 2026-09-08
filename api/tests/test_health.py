from fastapi.testclient import TestClient

from main import app
from tests.conftest import ORIGIN


def test_health_ok_without_auth():
    c = TestClient(app, raise_server_exceptions=False)
    resp = c.get("/api/health", headers=ORIGIN)
    assert resp.status_code == 200
    assert resp.json() == {"status": "ok"}


def test_health_still_behind_origin_guard(monkeypatch):
    # Cloud only: the guard is opt-in (ORIGIN_GUARD_ENABLED=true in
    # infra/lambda.tf), so the test has to turn it on the way the Lambda does.
    monkeypatch.setenv("ORIGIN_GUARD_ENABLED", "true")
    c = TestClient(app, raise_server_exceptions=False)
    resp = c.get("/api/health")  # no x-origin-token
    assert resp.status_code == 403
