import pytest
from fastapi.testclient import TestClient

from main import app
from tests.conftest import ORIGIN


@pytest.fixture
def public_recommended(monkeypatch):
    """Serve /api/recommended to logged-out visitors.

    Off by default — a selfhost instance exposes nothing without a login. The
    cloud deployment opts in via PUBLIC_RECOMMENDED_ENABLED=true in
    infra/lambda.tf, which is the configuration these tests exercise.
    """
    import routes.recommended as rec_module

    monkeypatch.setattr(rec_module, "PUBLIC_RECOMMENDED_ENABLED", True)


def _seed_game(fake_db, game_id: str = "01GAME"):
    fake_db["games"].seed(
        {
            "pk": game_id,
            "name": "Catan",
            "imageUrl": "https://img.example.com/catan.jpg",
            "tags": [],
            "createdAt": "2026-01-01T00:00:00Z",
        }
    )


def _seed_rec(fake_db, rec_id: str = "01REC", game_id: str = "01GAME"):
    fake_db["recs"].seed(
        {
            "pk": rec_id,
            "gamePk": game_id,
            "gameName": "Catan",
            "imageUrl": "https://img.example.com/catan.jpg",
            "blurb": "A classic!",
            "tags": ["Strategy"],
            "bestFor": "3–5 players",
            "order": 1,
            "createdAt": "2026-01-01T00:00:00Z",
        }
    )


def test_list_recommended_unauthenticated(fake_db, public_recommended):
    _seed_rec(fake_db)
    c = TestClient(app, raise_server_exceptions=False)
    response = c.get("/api/recommended", headers=ORIGIN)
    assert response.status_code == 200
    assert response.json()[0]["gameName"] == "Catan"


def test_list_recommended_sorted_by_order(fake_db, public_recommended):
    fake_db["recs"].seed(
        {
            **{
                "pk": "02REC",
                "gamePk": "01GAME",
                "gameName": "Catan",
                "imageUrl": "",
                "blurb": "B",
                "tags": [],
                "order": 2,
                "createdAt": "2026-01-01T00:00:00Z",
            }
        }
    )
    fake_db["recs"].seed(
        {
            **{
                "pk": "01REC",
                "gamePk": "01GAME",
                "gameName": "Catan",
                "imageUrl": "",
                "blurb": "A",
                "tags": [],
                "order": 1,
                "createdAt": "2026-01-01T00:00:00Z",
            }
        }
    )
    c = TestClient(app, raise_server_exceptions=False)
    response = c.get("/api/recommended", headers=ORIGIN)
    items = response.json()
    assert items[0]["order"] == 1
    assert items[1]["order"] == 2


def test_create_recommended_admin(authed_client, fake_db):
    _seed_game(fake_db)
    c = authed_client("admin")
    response = c.post(
        "/api/recommended",
        json={
            "gamePk": "01GAME",
            "blurb": "A classic!",
            "tags": ["Strategy"],
            "bestFor": "3–5 players",
            "order": 1,
        },
        headers=ORIGIN,
    )
    assert response.status_code == 201
    data = response.json()
    assert data["gameName"] == "Catan"
    assert data["blurb"] == "A classic!"
    assert data["imageUrl"] == "https://img.example.com/catan.jpg"
    assert "#" not in data["pk"]
    assert len(fake_db["recs"].scan()["Items"]) == 1


def test_create_recommended_game_not_found(authed_client, fake_db):
    c = authed_client("admin")
    response = c.post(
        "/api/recommended",
        json={"gamePk": "NONEXISTENT", "blurb": "test", "order": 0},
        headers=ORIGIN,
    )
    assert response.status_code == 404


def test_update_recommended_admin(authed_client, fake_db):
    _seed_rec(fake_db)
    c = authed_client("admin")
    response = c.put("/api/recommended/01REC", json={"blurb": "Updated!"}, headers=ORIGIN)
    assert response.status_code == 200
    assert response.json()["blurb"] == "Updated!"


def test_update_recommended_not_found(authed_client, fake_db):
    c = authed_client("admin")
    assert c.put("/api/recommended/MISSING", json={"blurb": "x"}, headers=ORIGIN).status_code == 404


def test_delete_recommended_admin(authed_client, fake_db):
    _seed_rec(fake_db)
    c = authed_client("admin")
    resp = c.delete("/api/recommended/01REC", headers=ORIGIN)
    assert resp.status_code == 204
    assert fake_db["recs"].get_item(Key={"pk": "01REC"}).get("Item") is None


def test_create_recommended_readonly_forbidden(authed_client, fake_db):
    _seed_game(fake_db)
    c = authed_client("readonly")
    resp = c.post(
        "/api/recommended",
        json={"gamePk": "01GAME", "blurb": "x", "order": 0},
        headers=ORIGIN,
    )
    assert resp.status_code == 403


def test_create_rec_empty_blurb_returns_422(authed_client, fake_db):
    fake_db["games"].seed(
        {
            "pk": "01GAME",
            "name": "Catan",
            "createdAt": "2026-01-01T00:00:00Z",
        }
    )
    c = authed_client("admin")
    resp = c.post(
        "/api/recommended",
        json={"gamePk": "01GAME", "blurb": "   "},
        headers=ORIGIN,
    )
    assert resp.status_code == 422


def test_update_rec_whitespace_blurb_returns_422(authed_client, fake_db):
    fake_db["recs"].seed(
        {
            "pk": "01REC",
            "gamePk": "01GAME",
            "blurb": "Original blurb",
            "createdAt": "2026-01-01T00:00:00Z",
            "order": 0,
        }
    )
    c = authed_client("admin")
    resp = c.put(
        "/api/recommended/01REC",
        json={"blurb": "   "},
        headers=ORIGIN,
    )
    assert resp.status_code == 422


def test_create_rec_empty_game_pk_returns_422(authed_client):
    c = authed_client("admin")
    resp = c.post(
        "/api/recommended",
        json={"gamePk": "", "blurb": "Great game"},
        headers=ORIGIN,
    )
    assert resp.status_code == 422


def test_get_recommended_detail_public(fake_db, public_recommended):
    _seed_rec(fake_db)
    c = TestClient(app, raise_server_exceptions=False)
    resp = c.get("/api/recommended/01REC", headers=ORIGIN)
    assert resp.status_code == 200
    assert resp.json()["gameName"] == "Catan"


def test_get_recommended_detail_not_found(fake_db, public_recommended):
    c = TestClient(app, raise_server_exceptions=False)
    resp = c.get("/api/recommended/MISSING", headers=ORIGIN)
    assert resp.status_code == 404


def test_get_recommended_detail_includes_content(fake_db, public_recommended):
    fake_db["recs"].seed(
        {
            "pk": "01REC",
            "gamePk": "01GAME",
            "gameName": "Catan",
            "imageUrl": "",
            "blurb": "A classic!",
            "tags": [],
            "order": 1,
            "createdAt": "2026-01-01T00:00:00Z",
            "content": "<p>Full review here.</p>",
        }
    )
    c = TestClient(app, raise_server_exceptions=False)
    resp = c.get("/api/recommended/01REC", headers=ORIGIN)
    assert resp.json()["content"] == "<p>Full review here.</p>"


def test_list_recommended_strips_content_injects_has_post(fake_db, public_recommended):
    fake_db["recs"].seed(
        {
            "pk": "01REC",
            "gamePk": "01GAME",
            "gameName": "Catan",
            "imageUrl": "",
            "blurb": "A classic!",
            "tags": [],
            "order": 1,
            "createdAt": "2026-01-01T00:00:00Z",
            "content": "<p>Full review.</p>",
        }
    )
    fake_db["recs"].seed(
        {
            "pk": "02REC",
            "gamePk": "01GAME",
            "gameName": "Ticket to Ride",
            "imageUrl": "",
            "blurb": "Great!",
            "tags": [],
            "order": 2,
            "createdAt": "2026-01-01T00:00:00Z",
        }
    )
    c = TestClient(app, raise_server_exceptions=False)
    resp = c.get("/api/recommended", headers=ORIGIN)
    items = {r["pk"]: r for r in resp.json()}
    assert "content" not in items["01REC"]
    assert items["01REC"]["hasPost"] is True
    assert items["02REC"]["hasPost"] is False


def test_create_recommended_denormalizes_bgg_metadata(authed_client, fake_db):
    fake_db["games"].seed(
        {
            "pk": "01GAME",
            "name": "Catan",
            "imageUrl": "https://img.example.com/catan.jpg",
            "minPlayers": 3,
            "maxPlayers": 5,
            "playTime": 90,
            "weight": 2.3,
            "yearPublished": 1995,
            "tags": [],
            "createdAt": "2026-01-01T00:00:00Z",
        }
    )
    c = authed_client("admin")
    resp = c.post(
        "/api/recommended",
        json={"gamePk": "01GAME", "blurb": "A classic!", "tags": [], "bestFor": "3-5", "order": 1},
        headers=ORIGIN,
    )
    assert resp.status_code == 201
    data = resp.json()
    assert data["minPlayers"] == 3
    assert data["maxPlayers"] == 5
    assert data["playTime"] == 90
    assert data["yearPublished"] == 1995


def test_update_recommended_content(authed_client, fake_db):
    _seed_rec(fake_db)
    c = authed_client("admin")
    resp = c.put(
        "/api/recommended/01REC",
        json={"content": "<p>My review.</p>"},
        headers=ORIGIN,
    )
    assert resp.status_code == 200
    assert resp.json()["content"] == "<p>My review.</p>"


def test_delete_nonexistent_rec_returns_404(authed_client, fake_db):
    c = authed_client("admin")
    resp = c.delete("/api/recommended/does-not-exist", headers=ORIGIN)
    assert resp.status_code == 404


def test_update_rec_explicit_null_clears_best_for(authed_client, fake_db):
    _seed_rec(fake_db)
    c = authed_client("admin")
    resp = c.put("/api/recommended/01REC", json={"bestFor": None}, headers=ORIGIN)
    assert resp.status_code == 200
    assert "bestFor" not in resp.json()


def test_update_rec_omitted_field_is_unchanged(authed_client, fake_db):
    _seed_rec(fake_db)
    c = authed_client("admin")
    resp = c.put("/api/recommended/01REC", json={"order": 5}, headers=ORIGIN)
    assert resp.status_code == 200
    assert resp.json()["bestFor"] == "3–5 players"
    assert resp.json()["order"] == 5


def test_update_rec_null_blurb_rejected(authed_client, fake_db):
    _seed_rec(fake_db)
    c = authed_client("admin")
    resp = c.put("/api/recommended/01REC", json={"blurb": None}, headers=ORIGIN)
    assert resp.status_code == 422


def test_list_recommended_requires_auth_when_public_disabled(monkeypatch, fake_db):
    import routes.recommended as rec_module

    monkeypatch.setattr(rec_module, "PUBLIC_RECOMMENDED_ENABLED", False)
    _seed_rec(fake_db)
    c = TestClient(app, raise_server_exceptions=False)
    resp = c.get("/api/recommended", headers=ORIGIN)
    assert resp.status_code == 401


def test_get_recommended_requires_auth_when_public_disabled(monkeypatch, fake_db):
    import routes.recommended as rec_module

    monkeypatch.setattr(rec_module, "PUBLIC_RECOMMENDED_ENABLED", False)
    _seed_rec(fake_db)
    c = TestClient(app, raise_server_exceptions=False)
    resp = c.get("/api/recommended/01REC", headers=ORIGIN)
    assert resp.status_code == 401


def test_list_recommended_authed_when_public_disabled(monkeypatch, fake_db, authed_client):
    import routes.recommended as rec_module

    monkeypatch.setattr(rec_module, "PUBLIC_RECOMMENDED_ENABLED", False)
    _seed_rec(fake_db)
    c = authed_client("readonly")
    resp = c.get("/api/recommended", headers=ORIGIN)
    assert resp.status_code == 200


def test_get_recommended_authed_when_public_disabled(monkeypatch, fake_db, authed_client):
    import routes.recommended as rec_module

    monkeypatch.setattr(rec_module, "PUBLIC_RECOMMENDED_ENABLED", False)
    _seed_rec(fake_db)
    c = authed_client("readonly")
    resp = c.get("/api/recommended/01REC", headers=ORIGIN)
    assert resp.status_code == 200
