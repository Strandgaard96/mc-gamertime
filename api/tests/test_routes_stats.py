from fastapi.testclient import TestClient

from main import app
from tests.conftest import ORIGIN


def test_stats_empty_db_returns_empty_leaderboard(authed_client, fake_db):
    c = authed_client("readonly")
    resp = c.get("/api/stats", headers=ORIGIN)
    assert resp.status_code == 200
    data = resp.json()
    assert data["leaderboard"] == []
    assert data["headToHead"] == []
    assert data["streaks"] == []
    assert data["mostPlayed"] is None
    assert data["perMonth"] == []


def test_stats_leaderboard_reflects_seeded_results(authed_client, fake_db):
    fake_db["results"].seed(
        {
            "pk": "01RESULT01",
            "gameId": "01GAME",
            "gameName": "Catan",
            "date": "2026-05-01",
            "players": [
                {"playerId": "alice", "playerName": "Alice"},
                {"playerId": "bob", "playerName": "Bob"},
            ],
            "winnerId": "alice",
            "winnerName": "Alice",
            "createdAt": "2026-05-01T00:00:00Z",
        }
    )
    fake_db["results"].seed(
        {
            "pk": "01RESULT02",
            "gameId": "01GAME",
            "gameName": "Catan",
            "date": "2026-05-08",
            "players": [
                {"playerId": "alice", "playerName": "Alice"},
                {"playerId": "bob", "playerName": "Bob"},
            ],
            "winnerId": "bob",
            "winnerName": "Bob",
            "createdAt": "2026-05-08T00:00:00Z",
        }
    )
    c = authed_client("readonly")
    resp = c.get("/api/stats", headers=ORIGIN)
    assert resp.status_code == 200
    data = resp.json()
    lb = data["leaderboard"]
    assert len(lb) == 2
    alice = next(e for e in lb if e["playerId"] == "alice")
    assert alice["wins"] == 1
    assert alice["played"] == 2
    assert alice["winRate"] == 0.5
    assert data["mostPlayed"]["gameName"] == "Catan"
    assert data["mostPlayed"]["count"] == 2


def test_stats_unauthenticated_returns_401():
    c = TestClient(app, raise_server_exceptions=False)
    resp = c.get("/api/stats", headers=ORIGIN)
    assert resp.status_code == 401


def test_get_stats_includes_variable_stats_for_configured_game(authed_client, fake_db):
    fake_db["games"].seed(
        {
            "pk": "01GAME",
            "name": "Chess",
            "createdAt": "2026-01-01T00:00:00Z",
            "playerVariables": [{"id": "color", "label": "Color", "options": ["White", "Black"]}],
        }
    )
    fake_db["results"].seed(
        {
            "pk": "01RESULT",
            "gameId": "01GAME",
            "gameName": "Chess",
            "date": "2026-01-01",
            "players": [
                {"playerId": "alice", "playerName": "Alice", "variables": {"color": "White"}},
                {"playerId": "bob", "playerName": "Bob", "variables": {"color": "Black"}},
            ],
            "winnerId": "alice",
            "winnerName": "Alice",
            "createdAt": "2026-01-01T00:00:00Z",
        }
    )
    c = authed_client("readonly")
    resp = c.get("/api/stats", headers=ORIGIN)
    assert resp.status_code == 200
    gs = next(g for g in resp.json()["gameStats"] if g["gameId"] == "01GAME")
    assert gs["variableStats"]["color"]["label"] == "Color"
    white = next(b for b in gs["variableStats"]["color"]["breakdown"] if b["value"] == "White")
    assert white["picks"] == 1
    assert white["wins"] == 1
