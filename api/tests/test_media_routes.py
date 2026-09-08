"""Uploaded media must require a session on every deployment.

Before this, the cloud deployment served /avatars/* and /blog-images/* straight
from S3 through CloudFront, so anyone who knew (or guessed — avatar keys are
just the username) a URL could fetch it without logging in.
"""

import importlib

from fastapi.testclient import TestClient

from lib import auth as auth_lib
from tests.conftest import (
    ORIGIN,
    TEST_JWT_SECRET,
    TEST_ORIGIN_TOKEN,
    make_auth_cookie,
)


def _client(monkeypatch, backend: str):
    monkeypatch.setenv("STORAGE_BACKEND", backend)
    monkeypatch.delenv("S3_ENDPOINT_URL", raising=False)
    monkeypatch.delenv("STATIC_DIR", raising=False)
    import main

    importlib.reload(main)
    # The autouse fixture in conftest primed the *previous* module object;
    # reloading resets that state, so mark the fresh one initialised too.
    main._origin_token = TEST_ORIGIN_TOKEN
    main._initialized = True
    auth_lib.set_jwt_secret(TEST_JWT_SECRET)
    return main


def test_media_routes_registered_on_cloud_backend(monkeypatch):
    main = _client(monkeypatch, "s3")
    try:
        paths = [r.path for r in main.app.routes]
        for prefix in ("/avatars", "/blog-images", "/game-images"):
            assert any(p.startswith(prefix) for p in paths), prefix
    finally:
        monkeypatch.delenv("STORAGE_BACKEND", raising=False)
        importlib.reload(main)


def test_avatar_requires_authentication(monkeypatch):
    main = _client(monkeypatch, "s3")
    try:
        client = TestClient(main.app, raise_server_exceptions=False)
        response = client.get("/avatars/alice.png", headers=ORIGIN)
        assert response.status_code == 401
    finally:
        monkeypatch.delenv("STORAGE_BACKEND", raising=False)
        importlib.reload(main)


def test_blog_image_requires_authentication(monkeypatch):
    main = _client(monkeypatch, "s3")
    try:
        client = TestClient(main.app, raise_server_exceptions=False)
        response = client.get("/blog-images/01ABC.png", headers=ORIGIN)
        assert response.status_code == 401
    finally:
        monkeypatch.delenv("STORAGE_BACKEND", raising=False)
        importlib.reload(main)


def test_media_route_rejects_other_prefixes(monkeypatch):
    # exports/ holds table dumps; it must not be reachable through this route
    # even with a valid session.
    main = _client(monkeypatch, "s3")
    try:
        client = TestClient(main.app, raise_server_exceptions=False)
        client.cookies.update(make_auth_cookie("readonly", "alice"))
        response = client.get("/avatars/../exports/boardsite-users.json", headers=ORIGIN)
        assert response.status_code in (400, 404)
    finally:
        monkeypatch.delenv("STORAGE_BACKEND", raising=False)
        importlib.reload(main)


def test_avatar_url_carries_cache_busting_stamp():
    from lib.storage import avatar_url

    assert avatar_url("alice", False) is None
    assert avatar_url("alice", True) == "/storage/avatars/alice.png"
    stamped = avatar_url("alice", True, "2026-08-20T12:34:56.789+00:00")
    assert stamped is not None
    assert stamped.startswith("/storage/avatars/alice.png?v=")
    # A later upload must produce a different URL, or browsers holding the old
    # image for the full max-age would keep showing it.
    assert stamped != avatar_url("alice", True, "2026-08-20T13:00:00.000+00:00")
