"""Responses must not be retained by anything between the browser and the app.

The threat model here is a shared cache or proxy on the network path, not the
user's own machine: API payloads carry per-user data, so nothing should hold a
copy, while uploaded media is deliberately reusable by the browser that
authenticated for it.
"""

from fastapi.testclient import TestClient

from main import app
from tests.conftest import ORIGIN

client = TestClient(app, raise_server_exceptions=False)


def test_api_responses_are_not_stored():
    response = client.get("/api/health", headers=ORIGIN)
    assert response.status_code == 200
    assert response.headers["cache-control"] == "no-store"


def test_api_error_responses_are_not_stored():
    # 401s from protected routes travel the same middleware path.
    response = client.get("/api/users", headers=ORIGIN)
    assert response.status_code == 401
    assert response.headers["cache-control"] == "no-store"


def test_non_api_responses_keep_their_own_caching():
    # The media route sets private/max-age itself; the blanket no-store must
    # not clobber it, or every avatar becomes a Lambda invocation per view.
    response = client.get("/avatars/nobody.png", headers=ORIGIN)
    assert response.headers.get("cache-control") != "no-store"
