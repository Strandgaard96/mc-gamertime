from tests.conftest import ORIGIN


def test_list_players_returns_public_user_info(authed_client, fake_db):
    fake_db["users"].seed(
        {
            "pk": "alice",
            "displayName": "Alice",
            "role": "admin",
            "createdAt": "2026-01-01T00:00:00Z",
            "passwordHash": "x",
        }
    )
    c = authed_client("readonly")
    resp = c.get("/api/players", headers=ORIGIN)
    assert resp.status_code == 200
    players = resp.json()
    alice = next(p for p in players if p["pk"] == "alice")
    assert alice["displayName"] == "Alice"
    assert "passwordHash" not in alice
    assert "role" not in alice


def test_list_players_unauthenticated(authed_client):
    from fastapi.testclient import TestClient

    from main import app

    c = TestClient(app, raise_server_exceptions=False)
    resp = c.get("/api/players", headers=ORIGIN)
    assert resp.status_code == 401


def test_create_player_route_does_not_exist(authed_client):
    c = authed_client("admin")
    resp = c.post("/api/players", json={"name": "Bob"}, headers=ORIGIN)
    assert resp.status_code == 405


def test_get_stats_unknown_player_returns_empty_stats(authed_client, fake_db):
    # No user row, no results → 200 with all-unearned achievements, empty stats
    c = authed_client("readonly")
    resp = c.get("/api/players/nonexistent-player-id/stats", headers=ORIGIN)
    assert resp.status_code == 200
    data = resp.json()
    assert data["perGameStats"] == []
    assert data["winRateTrend"] == []
    assert all(a["earnedAt"] is None for a in data["achievements"])


def test_player_stats_empty_db_returns_structure(authed_client, fake_db):
    fake_db["users"].seed(
        {
            "pk": "alice",
            "displayName": "Alice",
            "role": "readonly",
            "createdAt": "2026-01-01T00:00:00Z",
            "passwordHash": "x",
        }
    )
    c = authed_client("readonly")
    resp = c.get("/api/players/alice/stats", headers=ORIGIN)
    assert resp.status_code == 200
    data = resp.json()
    assert "achievements" in data
    assert "perGameStats" in data
    assert "winRateTrend" in data
    assert all(a["earnedAt"] is None for a in data["achievements"])
    assert data["perGameStats"] == []
    assert data["winRateTrend"] == []


def test_player_stats_achievement_earned(authed_client, fake_db):
    fake_db["users"].seed(
        {
            "pk": "alice",
            "displayName": "Alice",
            "role": "readonly",
            "createdAt": "2026-01-01T00:00:00Z",
            "passwordHash": "x",
        }
    )
    fake_db["results"].seed(
        {
            "pk": "result-01",
            "gameId": "game-01",
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
    c = authed_client("readonly")
    resp = c.get("/api/players/alice/stats", headers=ORIGIN)
    assert resp.status_code == 200
    data = resp.json()
    achievements = {a["id"]: a for a in data["achievements"]}
    assert achievements["first_win"]["earnedAt"] == "2026-05-01"


def test_player_stats_per_game_stats(authed_client, fake_db):
    fake_db["users"].seed(
        {
            "pk": "alice",
            "displayName": "Alice",
            "role": "readonly",
            "createdAt": "2026-01-01T00:00:00Z",
            "passwordHash": "x",
        }
    )
    fake_db["results"].seed(
        {
            "pk": "result-01",
            "gameId": "game-01",
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
            "pk": "result-02",
            "gameId": "game-01",
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
    resp = c.get("/api/players/alice/stats", headers=ORIGIN)
    assert resp.status_code == 200
    data = resp.json()
    assert len(data["perGameStats"]) == 1
    gs = data["perGameStats"][0]
    assert gs["gameId"] == "game-01"
    assert gs["wins"] == 1
    assert gs["played"] == 2
    assert gs["winRate"] == 0.5


def test_player_stats_win_rate_trend(authed_client, fake_db):
    fake_db["users"].seed(
        {
            "pk": "alice",
            "displayName": "Alice",
            "role": "readonly",
            "createdAt": "2026-01-01T00:00:00Z",
            "passwordHash": "x",
        }
    )
    fake_db["results"].seed(
        {
            "pk": "result-01",
            "gameId": "game-01",
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
    c = authed_client("readonly")
    resp = c.get("/api/players/alice/stats", headers=ORIGIN)
    assert resp.status_code == 200
    data = resp.json()
    assert len(data["winRateTrend"]) == 1
    assert data["winRateTrend"][0]["month"] == "2026-05"
    assert data["winRateTrend"][0]["winRate"] == 1.0


def test_player_stats_unauthenticated_returns_401():
    from fastapi.testclient import TestClient

    from main import app

    c = TestClient(app, raise_server_exceptions=False)
    resp = c.get("/api/players/alice/stats", headers=ORIGIN)
    assert resp.status_code == 401


def test_player_stats_heavyweight_achievement_via_route(authed_client, fake_db):
    fake_db["users"].seed(
        {
            "pk": "alice",
            "displayName": "Alice",
            "role": "readonly",
            "createdAt": "2026-01-01T00:00:00Z",
            "passwordHash": "x",
        }
    )
    fake_db["games"].seed(
        {
            "pk": "game-heavy",
            "name": "Gloomhaven",
            "weight": 4.5,
            "tags": [],
            "playerVariables": [],
            "createdAt": "2026-01-01T00:00:00Z",
        }
    )
    fake_db["results"].seed(
        {
            "pk": "result-01",
            "gameId": "game-heavy",
            "gameName": "Gloomhaven",
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
    c = authed_client("readonly")
    resp = c.get("/api/players/alice/stats", headers=ORIGIN)
    assert resp.status_code == 200
    achievements = {a["id"]: a for a in resp.json()["achievements"]}
    assert achievements["heavyweight"]["earnedAt"] == "2026-05-01"


def test_get_stats_removed_user_with_results_returns_200(authed_client, fake_db):
    # No user row seeded for "removed-user" — only a result referencing them
    fake_db["results"].seed(
        {
            "pk": "result-01",
            "gameId": "game-01",
            "gameName": "Catan",
            "date": "2026-05-01",
            "players": [
                {"playerId": "removed-user", "playerName": "Gone"},
                {"playerId": "bob", "playerName": "Bob"},
            ],
            "winnerId": "removed-user",
            "winnerName": "Gone",
            "createdAt": "2026-05-01T00:00:00Z",
        }
    )
    c = authed_client("readonly")
    resp = c.get("/api/players/removed-user/stats", headers=ORIGIN)
    assert resp.status_code == 200
    data = resp.json()
    assert len(data["perGameStats"]) == 1
    assert data["perGameStats"][0]["wins"] == 1
    assert data["perGameStats"][0]["played"] == 1
    assert len(data["winRateTrend"]) == 1
    assert data["winRateTrend"][0]["winRate"] == 1.0
