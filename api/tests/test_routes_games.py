from fastapi.testclient import TestClient

from main import app
from tests.conftest import ORIGIN


def test_create_game_missing_name_returns_422(authed_client):
    c = authed_client("admin")
    resp = c.post("/api/games", json={}, headers=ORIGIN)
    assert resp.status_code == 422


def test_create_game_success(authed_client, fake_db):
    c = authed_client("admin")
    resp = c.post("/api/games", json={"name": "Catan", "tags": ["Strategy"]}, headers=ORIGIN)
    assert resp.status_code == 201
    data = resp.json()
    assert data["name"] == "Catan"
    assert data["tags"] == ["Strategy"]
    assert "pk" in data
    assert "#" not in data["pk"]
    assert len(fake_db["games"].scan()["Items"]) == 1


def test_create_game_readonly_forbidden(authed_client):
    c = authed_client("readonly")
    resp = c.post("/api/games", json={"name": "Catan", "tags": []}, headers=ORIGIN)
    assert resp.status_code == 403


def test_create_game_rejects_unknown_fields(authed_client):
    c = authed_client("admin")
    resp = c.post(
        "/api/games",
        json={
            "name": "Catan",
            "tags": [],
            "pk": "evil-pk",
            "favorites": ["mallory"],
            "type": "haxx",
        },
        headers=ORIGIN,
    )
    assert resp.status_code == 422


def test_list_games_returns_seeded_items(authed_client, fake_db):
    fake_db["games"].seed(
        {
            "pk": "01TESTGAME",
            "name": "Catan",
            "tags": [],
            "createdAt": "2026-01-01T00:00:00Z",
        }
    )
    c = authed_client("readonly")
    resp = c.get("/api/games", headers=ORIGIN)
    assert resp.status_code == 200
    assert len(resp.json()) == 1
    assert resp.json()[0]["name"] == "Catan"


def test_list_games_unauthenticated():
    c = TestClient(app, raise_server_exceptions=False)
    resp = c.get("/api/games", headers=ORIGIN)
    assert resp.status_code == 401


def test_delete_game_removes_from_db(authed_client, fake_db):
    fake_db["games"].seed(
        {
            "pk": "01TESTGAME",
            "name": "Catan",
            "tags": [],
            "createdAt": "2026-01-01T00:00:00Z",
        }
    )
    c = authed_client("admin")
    resp = c.delete("/api/games/01TESTGAME", headers=ORIGIN)
    assert resp.status_code == 204
    assert fake_db["games"].get_item(Key={"pk": "01TESTGAME"}).get("Item") is None


def test_delete_nonexistent_game_returns_404(authed_client, fake_db):
    c = authed_client("admin")
    resp = c.delete("/api/games/does-not-exist", headers=ORIGIN)
    assert resp.status_code == 404


def test_delete_game_with_results_blocked_409(authed_client, fake_db):
    fake_db["games"].seed({"pk": "01GAME", "name": "Catan", "createdAt": "2026-01-01T00:00:00Z"})
    fake_db["results"].seed(
        {
            "pk": "01RESULT",
            "gameId": "01GAME",
            "gameName": "Catan",
            "date": "2026-01-01",
            "players": [],
            "winnerId": "a",
            "winnerName": "A",
            "createdAt": "2026-01-01T00:00:00Z",
        }
    )
    c = authed_client("admin")
    resp = c.delete("/api/games/01GAME", headers=ORIGIN)
    assert resp.status_code == 409
    assert "1 result" in resp.json()["detail"]


def test_delete_game_with_rec_blocked_409(authed_client, fake_db):
    fake_db["games"].seed({"pk": "01GAME", "name": "Catan", "createdAt": "2026-01-01T00:00:00Z"})
    fake_db["recs"].seed(
        {
            "pk": "01REC",
            "gamePk": "01GAME",
            "gameName": "Catan",
            "blurb": "x",
            "createdAt": "2026-01-01T00:00:00Z",
        }
    )
    c = authed_client("admin")
    resp = c.delete("/api/games/01GAME", headers=ORIGIN)
    assert resp.status_code == 409
    assert "1 recommendation" in resp.json()["detail"]


def test_delete_unreferenced_game_succeeds(authed_client, fake_db):
    fake_db["games"].seed({"pk": "01GAME", "name": "Catan", "createdAt": "2026-01-01T00:00:00Z"})
    c = authed_client("admin")
    resp = c.delete("/api/games/01GAME", headers=ORIGIN)
    assert resp.status_code == 204


def test_update_game_sets_player_variables_with_ids(authed_client, fake_db):
    fake_db["games"].seed(
        {"pk": "01GAME", "name": "Chess", "tags": [], "createdAt": "2026-01-01T00:00:00Z"}
    )
    c = authed_client("admin")
    resp = c.put(
        "/api/games/01GAME",
        json={
            "playerVariables": [{"label": "Color", "options": ["White", "Black"]}],
            "trackTurnOrder": True,
        },
        headers=ORIGIN,
    )
    assert resp.status_code == 200
    data = resp.json()
    assert data["playerVariables"] == [
        {"id": "color", "label": "Color", "options": ["White", "Black"]}
    ]
    assert data["trackTurnOrder"] is True
    assert data["name"] == "Chess"


def test_update_game_dedupes_variable_ids_for_duplicate_labels(authed_client, fake_db):
    fake_db["games"].seed(
        {"pk": "01GAME", "name": "Game", "tags": [], "createdAt": "2026-01-01T00:00:00Z"}
    )
    c = authed_client("admin")
    resp = c.put(
        "/api/games/01GAME",
        json={
            "playerVariables": [
                {"label": "Color", "options": ["Red", "Blue"]},
                {"label": "Color", "options": ["Green", "Yellow"]},
            ]
        },
        headers=ORIGIN,
    )
    assert resp.status_code == 200
    ids = [v["id"] for v in resp.json()["playerVariables"]]
    assert ids == ["color", "color-2"]


def test_update_game_player_variable_requires_two_options(authed_client, fake_db):
    fake_db["games"].seed(
        {"pk": "01GAME", "name": "Game", "tags": [], "createdAt": "2026-01-01T00:00:00Z"}
    )
    c = authed_client("admin")
    resp = c.put(
        "/api/games/01GAME",
        json={"playerVariables": [{"label": "Color", "options": ["White"]}]},
        headers=ORIGIN,
    )
    assert resp.status_code == 422


def test_update_game_rejects_id_in_player_variable_input(authed_client, fake_db):
    fake_db["games"].seed(
        {"pk": "01GAME", "name": "Game", "tags": [], "createdAt": "2026-01-01T00:00:00Z"}
    )
    c = authed_client("admin")
    resp = c.put(
        "/api/games/01GAME",
        json={
            "playerVariables": [{"id": "color", "label": "Color", "options": ["White", "Black"]}]
        },
        headers=ORIGIN,
    )
    assert resp.status_code == 422


def test_update_nonexistent_game_returns_404(authed_client):
    c = authed_client("admin")
    resp = c.put("/api/games/does-not-exist", json={"name": "X"}, headers=ORIGIN)
    assert resp.status_code == 404


def test_update_game_readonly_forbidden(authed_client, fake_db):
    fake_db["games"].seed(
        {"pk": "01GAME", "name": "Game", "tags": [], "createdAt": "2026-01-01T00:00:00Z"}
    )
    c = authed_client("readonly")
    resp = c.put("/api/games/01GAME", json={"name": "X"}, headers=ORIGIN)
    assert resp.status_code == 403


def test_update_game_partial_update_preserves_other_fields(authed_client, fake_db):
    fake_db["games"].seed(
        {
            "pk": "01GAME",
            "name": "Chess",
            "tags": ["Strategy"],
            "weight": 2.0,
            "createdAt": "2026-01-01T00:00:00Z",
        }
    )
    c = authed_client("admin")
    resp = c.put("/api/games/01GAME", json={"trackTurnOrder": True}, headers=ORIGIN)
    assert resp.status_code == 200
    data = resp.json()
    assert data["tags"] == ["Strategy"]
    assert data["weight"] == 2.0
    assert data["trackTurnOrder"] is True


def test_update_game_explicit_null_clears_field(authed_client, fake_db):
    fake_db["games"].seed(
        {
            "pk": "01GAME",
            "name": "Chess",
            "tags": ["Strategy"],
            "weight": 2.0,
            "yearPublished": 1475,
            "imageUrl": "https://example.com/chess.png",
            "createdAt": "2026-01-01T00:00:00Z",
        }
    )
    c = authed_client("admin")
    resp = c.put(
        "/api/games/01GAME", json={"yearPublished": None, "imageUrl": None}, headers=ORIGIN
    )
    assert resp.status_code == 200
    data = resp.json()
    assert data["yearPublished"] is None
    assert data["imageUrl"] is None
    assert data["weight"] == 2.0
    assert data["tags"] == ["Strategy"]


def test_update_game_strips_favorites_from_response_but_preserves_in_storage(
    authed_client, fake_db
):
    fake_db["games"].seed(
        {
            "pk": "01GAME",
            "name": "Chess",
            "tags": [],
            "createdAt": "2026-01-01T00:00:00Z",
            "favorites": {"alice"},
        }
    )
    c = authed_client("admin")
    resp = c.put("/api/games/01GAME", json={"trackTurnOrder": True}, headers=ORIGIN)
    assert resp.status_code == 200
    assert "favorites" not in resp.json()
    assert fake_db["games"].get_item(Key={"pk": "01GAME"})["Item"]["favorites"] == ["alice"]


def test_update_game_null_player_variables_normalizes_to_empty_list(authed_client, fake_db):
    fake_db["games"].seed(
        {
            "pk": "01GAME",
            "name": "Chess",
            "tags": [],
            "playerVariables": [{"id": "color", "label": "Color", "options": ["White", "Black"]}],
            "createdAt": "2026-01-01T00:00:00Z",
        }
    )
    c = authed_client("admin")
    resp = c.put("/api/games/01GAME", json={"playerVariables": None}, headers=ORIGIN)
    assert resp.status_code == 200
    assert resp.json()["playerVariables"] == []


def test_create_game_assigns_variable_ids(authed_client):
    c = authed_client("admin")
    resp = c.post(
        "/api/games",
        json={
            "name": "Terraforming Mars",
            "tags": [],
            "playerVariables": [{"label": "Corporation", "options": ["Saturn Systems", "Ecoline"]}],
        },
        headers=ORIGIN,
    )
    assert resp.status_code == 201
    assert resp.json()["playerVariables"] == [
        {"id": "corporation", "label": "Corporation", "options": ["Saturn Systems", "Ecoline"]}
    ]


def test_upload_url_extension_comes_from_content_type(authed_client, monkeypatch):
    import routes.games as games_module

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
    monkeypatch.setattr(games_module, "_s3", FakeS3())
    c = authed_client("admin")
    resp = c.post(
        "/api/games/upload",
        json={"filename": "evil.svg", "contentType": "image/png"},
        headers=ORIGIN,
    )
    assert resp.status_code == 200
    assert captured["key"].startswith("game-images/")
    assert captured["key"].endswith(".png")


def test_upload_url_rejects_unsupported_content_type(authed_client):
    c = authed_client("admin")
    resp = c.post(
        "/api/games/upload",
        json={"filename": "x.svg", "contentType": "image/svg+xml"},
        headers=ORIGIN,
    )
    assert resp.status_code == 422


def test_upload_url_readonly_forbidden(authed_client):
    c = authed_client("readonly")
    resp = c.post(
        "/api/games/upload",
        json={"contentType": "image/png"},
        headers=ORIGIN,
    )
    assert resp.status_code == 403
