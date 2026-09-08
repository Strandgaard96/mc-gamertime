from tests.conftest import ORIGIN, make_auth_cookie


def test_add_favorite_succeeds(fake_db):
    from fastapi.testclient import TestClient

    from main import app

    fake_db["games"].seed({"pk": "01GAME", "name": "Wingspan"})
    c = TestClient(app, raise_server_exceptions=False)
    c.cookies.set("token", make_auth_cookie("readonly")["token"])  # sub="testuser"

    resp = c.post("/api/games/01GAME/favorite", headers=ORIGIN)

    assert resp.status_code == 204
    assert fake_db["games"].get_item(Key={"pk": "01GAME"})["Item"]["favorites"] == ["testuser"]


def test_remove_favorite_succeeds(fake_db):
    from fastapi.testclient import TestClient

    from main import app

    fake_db["games"].seed({"pk": "01GAME", "name": "Wingspan", "favorites": {"testuser"}})
    c = TestClient(app, raise_server_exceptions=False)
    c.cookies.set("token", make_auth_cookie("readonly")["token"])

    resp = c.delete("/api/games/01GAME/favorite", headers=ORIGIN)

    assert resp.status_code == 204
    assert fake_db["games"].get_item(Key={"pk": "01GAME"})["Item"]["favorites"] == []


def test_add_favorite_missing_game_returns_404(fake_db):
    from fastapi.testclient import TestClient

    from main import app

    c = TestClient(app, raise_server_exceptions=False)
    c.cookies.set("token", make_auth_cookie("readonly")["token"])

    resp = c.post("/api/games/nonexistent/favorite", headers=ORIGIN)

    assert resp.status_code == 404
