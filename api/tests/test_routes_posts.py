from fastapi.testclient import TestClient

from main import app
from tests.conftest import ORIGIN


def _seed_post(fake_db, post_id: str = "01POST"):
    fake_db["posts"].seed(
        {
            "pk": post_id,
            "title": "Great game night",
            "content": "<p>We played Catan!</p>",
            "sessionPk": "01RESULT",
            "gameName": "Catan",
            "gamePk": "01GAME",
            "createdAt": "2026-01-01T00:00:00Z",
            "authorName": "Magnus",
        }
    )


def test_list_posts_authenticated(authed_client, fake_db):
    _seed_post(fake_db)
    c = authed_client("readonly")
    resp = c.get("/api/posts", headers=ORIGIN)
    assert resp.status_code == 200
    assert resp.json()[0]["title"] == "Great game night"


def test_list_posts_unauthenticated():
    c = TestClient(app, raise_server_exceptions=False)
    assert c.get("/api/posts", headers=ORIGIN).status_code == 401


def test_get_post_authenticated(authed_client, fake_db):
    _seed_post(fake_db, "01TESTPOST")
    c = authed_client("readonly")
    resp = c.get("/api/posts/01TESTPOST", headers=ORIGIN)
    assert resp.status_code == 200
    assert resp.json()["title"] == "Great game night"


def test_get_post_not_found(authed_client, fake_db):
    c = authed_client("readonly")
    assert c.get("/api/posts/MISSING", headers=ORIGIN).status_code == 404


def test_create_post_admin(authed_client, fake_db):
    c = authed_client("admin")
    resp = c.post(
        "/api/posts",
        json={
            "title": "Great game night",
            "content": "<p>We played Catan!</p>",
            "sessionPk": "01RESULT",
            "gameName": "Catan",
            "gamePk": "01GAME",
        },
        headers=ORIGIN,
    )
    assert resp.status_code == 201
    data = resp.json()
    assert data["title"] == "Great game night"
    assert "#" not in data["pk"]
    assert len(fake_db["posts"].scan()["Items"]) == 1


def test_create_post_readonly_forbidden(authed_client):
    c = authed_client("readonly")
    resp = c.post(
        "/api/posts",
        json={"title": "T", "content": "x"},
        headers=ORIGIN,
    )
    assert resp.status_code == 403


def test_update_post_admin(authed_client, fake_db):
    _seed_post(fake_db, "01TESTPOST")
    c = authed_client("admin")
    resp = c.put(
        "/api/posts/01TESTPOST",
        json={"title": "Updated title"},
        headers=ORIGIN,
    )
    assert resp.status_code == 200
    assert resp.json()["title"] == "Updated title"


def test_update_post_not_found(authed_client, fake_db):
    c = authed_client("admin")
    assert c.put("/api/posts/MISSING", json={"title": "x"}, headers=ORIGIN).status_code == 404


def test_delete_post_admin(authed_client, fake_db):
    _seed_post(fake_db, "01TESTPOST")
    c = authed_client("admin")
    resp = c.delete("/api/posts/01TESTPOST", headers=ORIGIN)
    assert resp.status_code == 204
    assert fake_db["posts"].get_item(Key={"pk": "01TESTPOST"}).get("Item") is None


def test_delete_post_not_found(authed_client, fake_db):
    c = authed_client("admin")
    assert c.delete("/api/posts/MISSING", headers=ORIGIN).status_code == 404


def test_create_post_empty_title_returns_422(authed_client):
    c = authed_client("admin")
    resp = c.post(
        "/api/posts",
        json={
            "title": "  ",
            "content": "<p>hello</p>",
        },
        headers=ORIGIN,
    )
    assert resp.status_code == 422


def test_create_post_empty_content_returns_422(authed_client):
    c = authed_client("admin")
    resp = c.post(
        "/api/posts",
        json={
            "title": "My Post",
            "content": "  ",
        },
        headers=ORIGIN,
    )
    assert resp.status_code == 422


def test_update_post_explicit_null_clears_session_pk(authed_client, fake_db):
    _seed_post(fake_db, "01TESTPOST")
    c = authed_client("admin")
    resp = c.put("/api/posts/01TESTPOST", json={"sessionPk": None}, headers=ORIGIN)
    assert resp.status_code == 200
    assert "sessionPk" not in resp.json()


def test_update_post_omitted_field_is_unchanged(authed_client, fake_db):
    _seed_post(fake_db, "01TESTPOST")
    c = authed_client("admin")
    resp = c.put("/api/posts/01TESTPOST", json={"title": "New title"}, headers=ORIGIN)
    assert resp.status_code == 200
    assert resp.json()["sessionPk"] == "01RESULT"


def test_update_post_null_title_rejected(authed_client, fake_db):
    _seed_post(fake_db, "01TESTPOST")
    c = authed_client("admin")
    resp = c.put("/api/posts/01TESTPOST", json={"title": None}, headers=ORIGIN)
    assert resp.status_code == 422


def test_upload_url_extension_comes_from_content_type_not_filename(authed_client, monkeypatch):
    import routes.posts as posts_module

    # Presigned uploads are the S3 path; the default local backend returns a
    # /storage proxy URL instead.
    monkeypatch.setenv("STORAGE_BACKEND", "s3")
    captured = {}

    class FakeS3:
        def generate_presigned_url(self, op, Params, ExpiresIn):
            captured["key"] = Params["Key"]
            return "https://example.com/upload"

    # _s3 is built at import time, when the default local backend was still in
    # effect — replace the client itself, not one of its attributes.
    monkeypatch.setattr(posts_module, "_s3", FakeS3())
    c = authed_client("admin")
    resp = c.post(
        "/api/posts/upload",
        json={"filename": "evil.svg", "contentType": "image/png"},
        headers=ORIGIN,
    )
    assert resp.status_code == 200
    assert captured["key"].endswith(".png")


def test_generate_upload_url_selfhost_returns_storage_path(monkeypatch):
    import routes.posts as posts_module

    monkeypatch.setattr(posts_module, "_OBJECT_BASE_URL", "/storage")
    monkeypatch.setenv("S3_ENDPOINT_URL", "http://seaweedfs:8333")

    upload_url, image_url = posts_module.generate_upload_url("image/png")

    assert upload_url == image_url
    assert upload_url.startswith("/storage/blog-images/")
    assert upload_url.endswith(".png")


def test_generate_upload_url_storage_backend_local_returns_storage_path(monkeypatch):
    import routes.posts as posts_module

    monkeypatch.setattr(posts_module, "_OBJECT_BASE_URL", "/storage")
    monkeypatch.delenv("S3_ENDPOINT_URL", raising=False)
    monkeypatch.setenv("STORAGE_BACKEND", "local")

    upload_url, image_url = posts_module.generate_upload_url("image/png")

    assert upload_url == image_url
    assert upload_url.startswith("/storage/blog-images/")
