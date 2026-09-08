from tests.conftest import ORIGIN


def _seed_notification(fake_db, **overrides):
    item = {
        "pk": "01NOTIF",
        "playerId": "testuser",
        "achievementId": "first_win",
        "label": "First Blood",
        "icon": "🏆",
        "description": "Won your first game",
        "gameId": "01GAME",
        "gameName": "Catan",
        "resultId": "01RESULT",
        "createdAt": "2026-01-01T00:00:00+00:00",
        **overrides,
    }
    fake_db["notifications"].seed(item)
    return item


def test_list_notifications_empty(authed_client):
    c = authed_client("admin")
    resp = c.get("/api/notifications", headers=ORIGIN)
    assert resp.status_code == 200
    assert resp.json() == {"notifications": [], "unreadCount": 0}


def test_list_notifications_unread_count_without_last_read_at(authed_client, fake_db):
    _seed_notification(fake_db)
    c = authed_client("admin")
    resp = c.get("/api/notifications", headers=ORIGIN)
    assert resp.status_code == 200
    data = resp.json()
    assert len(data["notifications"]) == 1
    assert data["unreadCount"] == 1


def test_list_notifications_only_returns_own(authed_client, fake_db):
    _seed_notification(fake_db, pk="01NOTIF-MINE", playerId="testuser")
    _seed_notification(fake_db, pk="01NOTIF-OTHER", playerId="someoneelse")
    c = authed_client("admin")
    resp = c.get("/api/notifications", headers=ORIGIN)
    pks = [n["pk"] for n in resp.json()["notifications"]]
    assert pks == ["01NOTIF-MINE"]


def test_mark_notifications_read_clears_unread_count(authed_client, fake_db):
    _seed_notification(fake_db, createdAt="2026-01-01T00:00:00+00:00")
    c = authed_client("admin")

    resp = c.post("/api/notifications/read", headers=ORIGIN)
    assert resp.status_code == 204

    resp = c.get("/api/notifications", headers=ORIGIN)
    assert resp.json()["unreadCount"] == 0
    # The notification itself is still returned, just not counted as unread
    assert len(resp.json()["notifications"]) == 1


def test_notifications_requires_auth():
    from fastapi.testclient import TestClient

    from main import app

    c = TestClient(app, raise_server_exceptions=False)
    resp = c.get("/api/notifications", headers=ORIGIN)
    assert resp.status_code == 401
