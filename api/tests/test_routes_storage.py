import pytest
from fastapi import FastAPI, HTTPException
from fastapi.testclient import TestClient

import routes.storage as storage_module
from lib.auth import AuthUser
from tests.conftest import make_auth_cookie


def _make_app() -> FastAPI:
    app = FastAPI()
    app.include_router(storage_module.router, prefix="/storage")
    return app


# --- _reject_path_traversal (unit-level, avoids URL-normalization edge cases) ---


def test_reject_path_traversal_rejects_dotdot():
    with pytest.raises(HTTPException) as exc_info:
        storage_module._reject_path_traversal("avatars/../secrets.json")
    assert exc_info.value.status_code == 400


def test_reject_path_traversal_rejects_leading_slash():
    with pytest.raises(HTTPException) as exc_info:
        storage_module._reject_path_traversal("/etc/passwd")
    assert exc_info.value.status_code == 400


def test_reject_path_traversal_allows_normal_path():
    storage_module._reject_path_traversal("avatars/alice.png")  # no exception


# --- GET /storage/{path} ---


def test_get_object_requires_auth(fake_db):
    app = _make_app()
    c = TestClient(app, raise_server_exceptions=False)
    resp = c.get("/storage/avatars/alice.png")
    assert resp.status_code == 401


def test_get_object_rejects_disallowed_prefix(fake_db):
    app = _make_app()
    c = TestClient(app, raise_server_exceptions=False)
    c.cookies.set("token", make_auth_cookie("readonly")["token"])
    resp = c.get("/storage/exports/2026-06-15/boardsite-users.json")
    assert resp.status_code == 404


def test_get_object_streams_allowed_prefix(fake_db, monkeypatch):
    class FakeBody:
        def iter_chunks(self):
            yield b"image-bytes"

    class FakeS3:
        def get_object(self, Bucket, Key):
            assert Key == "avatars/alice.png"
            return {"Body": FakeBody(), "ContentType": "image/png"}

    monkeypatch.setattr(storage_module, "make_s3_client", lambda: FakeS3())

    app = _make_app()
    c = TestClient(app, raise_server_exceptions=False)
    c.cookies.set("token", make_auth_cookie("readonly")["token"])
    resp = c.get("/storage/avatars/alice.png")

    assert resp.status_code == 200
    assert resp.content == b"image-bytes"
    assert resp.headers["content-type"] == "image/png"


def test_get_object_not_found_in_store(fake_db, monkeypatch):
    from botocore.exceptions import ClientError

    class FakeS3:
        def get_object(self, Bucket, Key):
            raise ClientError({"Error": {"Code": "NoSuchKey", "Message": "x"}}, "GetObject")

    monkeypatch.setattr(storage_module, "make_s3_client", lambda: FakeS3())

    app = _make_app()
    c = TestClient(app, raise_server_exceptions=False)
    c.cookies.set("token", make_auth_cookie("readonly")["token"])
    resp = c.get("/storage/avatars/missing.png")

    assert resp.status_code == 404


# --- _authorize_write (unit-level) ---


def test_authorize_write_avatar_own_allowed():
    user = AuthUser(sub="alice", role="readonly", displayName="Alice")
    storage_module._authorize_write("avatars/alice.png", user)  # no exception


def test_authorize_write_avatar_other_user_forbidden():
    user = AuthUser(sub="alice", role="readonly", displayName="Alice")
    with pytest.raises(HTTPException) as exc_info:
        storage_module._authorize_write("avatars/bob.png", user)
    assert exc_info.value.status_code == 403


def test_authorize_write_avatar_admin_can_write_any():
    user = AuthUser(sub="admin", role="admin", displayName="Admin")
    storage_module._authorize_write("avatars/bob.png", user)  # no exception


def test_authorize_write_blog_image_requires_admin():
    user = AuthUser(sub="alice", role="readonly", displayName="Alice")
    with pytest.raises(HTTPException) as exc_info:
        storage_module._authorize_write("blog-images/01ABC.png", user)
    assert exc_info.value.status_code == 403


def test_authorize_write_blog_image_admin_allowed():
    user = AuthUser(sub="admin", role="admin", displayName="Admin")
    storage_module._authorize_write("blog-images/01ABC.png", user)  # no exception


def test_authorize_write_game_image_requires_admin():
    user = AuthUser(sub="alice", role="readonly", displayName="Alice")
    with pytest.raises(HTTPException) as exc_info:
        storage_module._authorize_write("game-images/01ABC.png", user)
    assert exc_info.value.status_code == 403


def test_authorize_write_game_image_admin_allowed():
    user = AuthUser(sub="admin", role="admin", displayName="Admin")
    storage_module._authorize_write("game-images/01ABC.png", user)  # no exception


# --- PUT /storage/{path} ---


def test_put_object_requires_auth(fake_db):
    app = _make_app()
    c = TestClient(app, raise_server_exceptions=False)
    resp = c.put("/storage/blog-images/foo.png", content=b"data")
    assert resp.status_code == 401


def test_put_object_rejects_disallowed_prefix(fake_db):
    app = _make_app()
    c = TestClient(app, raise_server_exceptions=False)
    c.cookies.set("token", make_auth_cookie("readonly")["token"])
    resp = c.put("/storage/exports/2026-06-15/boardsite-users.json", content=b"data")
    assert resp.status_code == 403


def test_put_object_avatar_other_user_forbidden(fake_db):
    app = _make_app()
    c = TestClient(app, raise_server_exceptions=False)
    c.cookies.set("token", make_auth_cookie("readonly")["token"])  # sub="testuser"
    resp = c.put(
        "/storage/avatars/someoneelse.png",
        content=b"\x89PNG",
        headers={"content-type": "image/png"},
    )
    assert resp.status_code == 403


def test_put_object_blog_image_readonly_forbidden(fake_db):
    app = _make_app()
    c = TestClient(app, raise_server_exceptions=False)
    c.cookies.set("token", make_auth_cookie("readonly")["token"])
    resp = c.put(
        "/storage/blog-images/01ABC.png",
        content=b"\x89PNG",
        headers={"content-type": "image/png"},
    )
    assert resp.status_code == 403


def test_put_object_rejects_unsupported_content_type(fake_db):
    app = _make_app()
    c = TestClient(app, raise_server_exceptions=False)
    c.cookies.set("token", make_auth_cookie("admin")["token"])
    resp = c.put(
        "/storage/blog-images/01ABC.svg",
        content=b"<svg/>",
        headers={"content-type": "image/svg+xml"},
    )
    assert resp.status_code == 415


def test_put_object_rejects_oversized_body(fake_db, monkeypatch):
    monkeypatch.setattr(storage_module, "_MAX_UPLOAD_BYTES", 10)
    app = _make_app()
    c = TestClient(app, raise_server_exceptions=False)
    c.cookies.set("token", make_auth_cookie("admin")["token"])
    resp = c.put(
        "/storage/blog-images/01ABC.png",
        content=b"x" * 11,
        headers={"content-type": "image/png"},
    )
    assert resp.status_code == 413


def test_put_object_blog_image_admin_succeeds(fake_db, monkeypatch):
    captured = {}

    class FakeS3:
        def put_object(self, **kwargs):
            captured.update(kwargs)

    monkeypatch.setattr(storage_module, "make_s3_client", lambda: FakeS3())
    monkeypatch.setattr(storage_module, "_BUCKET", "test-bucket")

    app = _make_app()
    c = TestClient(app, raise_server_exceptions=False)
    c.cookies.set("token", make_auth_cookie("admin")["token"])
    resp = c.put(
        "/storage/blog-images/01ABC.png",
        content=b"binary-data",
        headers={"content-type": "image/png"},
    )

    assert resp.status_code == 200
    assert captured["Bucket"] == "test-bucket"
    assert captured["Key"] == "blog-images/01ABC.png"
    assert captured["Body"] == b"binary-data"
    assert captured["ContentType"] == "image/png"


def test_put_object_game_image_admin_succeeds(fake_db, monkeypatch):
    captured = {}

    class FakeS3:
        def put_object(self, **kwargs):
            captured.update(kwargs)

    monkeypatch.setattr(storage_module, "make_s3_client", lambda: FakeS3())
    monkeypatch.setattr(storage_module, "_BUCKET", "test-bucket")

    app = _make_app()
    c = TestClient(app, raise_server_exceptions=False)
    c.cookies.set("token", make_auth_cookie("admin")["token"])
    resp = c.put(
        "/storage/game-images/01ABC.png",
        content=b"binary-data",
        headers={"content-type": "image/png"},
    )

    assert resp.status_code == 200
    assert captured["Key"] == "game-images/01ABC.png"


def test_put_object_game_image_readonly_forbidden(fake_db):
    app = _make_app()
    c = TestClient(app, raise_server_exceptions=False)
    c.cookies.set("token", make_auth_cookie("readonly")["token"])
    resp = c.put(
        "/storage/game-images/01ABC.png",
        content=b"\x89PNG",
        headers={"content-type": "image/png"},
    )
    assert resp.status_code == 403


def test_put_object_avatar_own_succeeds(fake_db, monkeypatch):
    captured = {}

    class FakeS3:
        def put_object(self, **kwargs):
            captured.update(kwargs)

    monkeypatch.setattr(storage_module, "make_s3_client", lambda: FakeS3())
    monkeypatch.setattr(storage_module, "_BUCKET", "test-bucket")

    app = _make_app()
    c = TestClient(app, raise_server_exceptions=False)
    c.cookies.set("token", make_auth_cookie("readonly")["token"])  # sub="testuser"
    resp = c.put(
        "/storage/avatars/testuser.png",
        content=b"binary-data",
        headers={"content-type": "image/png"},
    )

    assert resp.status_code == 200
    assert captured["Key"] == "avatars/testuser.png"
