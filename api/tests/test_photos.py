import pytest
from fastapi.testclient import TestClient
from ulid import ULID

import routes.photos as photos_module
from main import app
from tests.conftest import ORIGIN, make_auth_cookie


class FakeS3:
    def __init__(self):
        self.deleted: list[str] = []

    def delete_object(self, *, Bucket: str, Key: str) -> None:
        self.deleted.append(Key)


@pytest.fixture
def fake_s3(monkeypatch):
    s3 = FakeS3()
    monkeypatch.setattr(photos_module, "_s3", s3)
    return s3


def _seed_session(fake_db, pk="s1"):
    fake_db["results"].seed(
        {
            "pk": pk,
            "gameId": "g1",
            "gameName": "Catan",
            "date": "2026-06-01",
            "players": [],
            "winnerId": "testuser",
            "winnerName": "Test User",
            "createdAt": "2026-06-01T00:00:00Z",
        }
    )


def _key(ext="webp") -> str:
    return f"session-photos/{ULID()!s}.{ext}"


def _seed_photo(fake_db, pk, session="s1", uploader="testuser", key=None):
    fake_db["reactions"].seed(
        {
            "pk": pk,
            "type": "photo",
            "sessionPk": session,
            "key": key or _key(),
            "imageUrl": "/storage/x",
            "uploaderId": uploader,
            "uploaderName": uploader.title(),
            "createdAt": "2026-06-01T00:00:00Z",
        }
    )


def _client_as(sub: str, role: str = "readonly") -> TestClient:
    c = TestClient(app, raise_server_exceptions=False)
    c.cookies.set("token", make_auth_cookie(role, sub=sub)["token"])
    return c


def test_readonly_can_request_upload_and_confirm(authed_client, fake_db):
    _seed_session(fake_db)
    c = authed_client("readonly")
    up = c.post(
        "/api/photos/upload", json={"sessionPk": "s1", "contentType": "image/webp"}, headers=ORIGIN
    )
    assert up.status_code == 200
    body = up.json()
    assert body["key"].startswith("session-photos/")
    assert body["key"].endswith(".webp")

    created = c.post("/api/photos", json={"sessionPk": "s1", "key": body["key"]}, headers=ORIGIN)
    assert created.status_code == 201
    row = created.json()
    assert row["type"] == "photo"
    assert row["uploaderId"] == "testuser"
    assert row["imageUrl"].endswith(body["key"])  # server-derived from key


def test_upload_unsupported_type_422(authed_client, fake_db):
    _seed_session(fake_db)
    c = authed_client("readonly")
    resp = c.post(
        "/api/photos/upload", json={"sessionPk": "s1", "contentType": "image/gif"}, headers=ORIGIN
    )
    assert resp.status_code == 422


def test_upload_unknown_session_404(authed_client, fake_db):
    c = authed_client("readonly")
    resp = c.post(
        "/api/photos/upload",
        json={"sessionPk": "nope", "contentType": "image/webp"},
        headers=ORIGIN,
    )
    assert resp.status_code == 404


def test_upload_and_confirm_capped_at_six(authed_client, fake_db):
    _seed_session(fake_db)
    for i in range(6):
        _seed_photo(fake_db, f"p{i}")
    c = authed_client("readonly")
    up = c.post(
        "/api/photos/upload", json={"sessionPk": "s1", "contentType": "image/webp"}, headers=ORIGIN
    )
    assert up.status_code == 409
    confirm = c.post("/api/photos", json={"sessionPk": "s1", "key": _key()}, headers=ORIGIN)
    assert confirm.status_code == 409


def test_confirm_bad_key_422(authed_client, fake_db):
    _seed_session(fake_db)
    c = authed_client("readonly")
    for key in ("avatars/testuser.png", "session-photos/../x.png", "session-photos/abc.webp"):
        resp = c.post("/api/photos", json={"sessionPk": "s1", "key": key}, headers=ORIGIN)
        assert resp.status_code == 422, key


def test_confirm_duplicate_key_409(authed_client, fake_db):
    _seed_session(fake_db)
    key = _key()
    _seed_photo(fake_db, "p1", key=key)
    c = authed_client("readonly")
    resp = c.post("/api/photos", json={"sessionPk": "s1", "key": key}, headers=ORIGIN)
    assert resp.status_code == 409


def test_confirm_unknown_session_404(authed_client, fake_db):
    c = authed_client("readonly")
    resp = c.post("/api/photos", json={"sessionPk": "nope", "key": _key()}, headers=ORIGIN)
    assert resp.status_code == 404


def test_owner_deletes_photo_and_object(fake_db, fake_s3):
    _seed_session(fake_db)
    key = _key()
    _seed_photo(fake_db, "p1", uploader="alice", key=key)
    resp = _client_as("alice").delete("/api/photos/p1", headers=ORIGIN)
    assert resp.status_code == 204
    assert fake_s3.deleted == [key]
    assert fake_db["reactions"].get_item(Key={"pk": "p1"}).get("Item") is None


def test_admin_deletes_any_photo(fake_db, fake_s3):
    _seed_session(fake_db)
    _seed_photo(fake_db, "p1", uploader="alice")
    resp = _client_as("root", role="admin").delete("/api/photos/p1", headers=ORIGIN)
    assert resp.status_code == 204


def test_other_user_cannot_delete_404(fake_db, fake_s3):
    _seed_session(fake_db)
    _seed_photo(fake_db, "p1", uploader="alice")
    resp = _client_as("bob").delete("/api/photos/p1", headers=ORIGIN)
    assert resp.status_code == 404
    assert fake_s3.deleted == []


def test_delete_comment_id_via_photos_404(fake_db, fake_s3):
    fake_db["reactions"].seed(
        {
            "pk": "c1",
            "type": "comment",
            "sessionPk": "s1",
            "authorId": "alice",
            "authorName": "Alice",
            "text": "hi",
            "createdAt": "2026-06-01T00:00:00Z",
        }
    )
    resp = _client_as("alice").delete("/api/photos/c1", headers=ORIGIN)
    assert resp.status_code == 404


def test_result_delete_cascades_photos(authed_client, fake_db, fake_s3):
    _seed_session(fake_db)
    k1, k2 = _key(), _key("jpg")
    _seed_photo(fake_db, "p1", key=k1)
    _seed_photo(fake_db, "p2", key=k2)
    _seed_photo(fake_db, "p3", session="other")
    c = authed_client("admin")
    assert c.delete("/api/results/s1", headers=ORIGIN).status_code == 204
    assert sorted(fake_s3.deleted) == sorted([k1, k2])
    assert fake_db["reactions"].get_item(Key={"pk": "p3"}).get("Item") is not None
