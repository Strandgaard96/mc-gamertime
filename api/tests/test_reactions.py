from tests.conftest import ORIGIN, make_auth_cookie


def _seed_session(fake_db, pk="session1"):
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


def test_list_reactions_empty(authed_client):
    c = authed_client("readonly")
    resp = c.get("/api/reactions", headers=ORIGIN)
    assert resp.status_code == 200
    assert resp.json() == []


def test_list_reactions_returns_seeded_items(authed_client, fake_db):
    fake_db["reactions"].seed(
        {
            "pk": "r1",
            "type": "reaction",
            "sessionPk": "session1",
            "emoji": "👍",
            "userId": "testuser",
            "userName": "Test User",
            "createdAt": "2026-06-01T00:00:00Z",
        }
    )
    c = authed_client("readonly")
    resp = c.get("/api/reactions", headers=ORIGIN)
    assert resp.status_code == 200
    body = resp.json()
    assert len(body) == 1
    assert body[0]["emoji"] == "👍"


def test_toggle_reaction_unknown_session_returns_404(authed_client):
    c = authed_client("readonly")
    resp = c.post(
        "/api/reactions/toggle", json={"sessionPk": "missing", "emoji": "👍"}, headers=ORIGIN
    )
    assert resp.status_code == 404


def test_toggle_reaction_invalid_emoji_returns_422(authed_client, fake_db):
    _seed_session(fake_db)
    c = authed_client("readonly")
    resp = c.post(
        "/api/reactions/toggle", json={"sessionPk": "session1", "emoji": "🦄"}, headers=ORIGIN
    )
    assert resp.status_code == 422


def test_toggle_reaction_adds_then_removes(authed_client, fake_db):
    _seed_session(fake_db)
    c = authed_client("readonly")

    resp1 = c.post(
        "/api/reactions/toggle", json={"sessionPk": "session1", "emoji": "👍"}, headers=ORIGIN
    )
    assert resp1.status_code == 200
    assert resp1.json()["action"] == "added"
    assert len(c.get("/api/reactions", headers=ORIGIN).json()) == 1

    resp2 = c.post(
        "/api/reactions/toggle", json={"sessionPk": "session1", "emoji": "👍"}, headers=ORIGIN
    )
    assert resp2.status_code == 200
    assert resp2.json()["action"] == "removed"
    assert c.get("/api/reactions", headers=ORIGIN).json() == []


def test_create_comment(authed_client, fake_db):
    _seed_session(fake_db)
    c = authed_client("readonly")
    resp = c.post(
        "/api/comments", json={"sessionPk": "session1", "text": "Great game!"}, headers=ORIGIN
    )
    assert resp.status_code == 201
    body = resp.json()
    assert body["text"] == "Great game!"
    assert body["authorId"] == "testuser"
    assert body["type"] == "comment"


def test_create_comment_empty_text_returns_422(authed_client, fake_db):
    _seed_session(fake_db)
    c = authed_client("readonly")
    resp = c.post("/api/comments", json={"sessionPk": "session1", "text": "   "}, headers=ORIGIN)
    assert resp.status_code == 422


def test_create_comment_too_long_returns_422(authed_client, fake_db):
    _seed_session(fake_db)
    c = authed_client("readonly")
    resp = c.post(
        "/api/comments", json={"sessionPk": "session1", "text": "x" * 501}, headers=ORIGIN
    )
    assert resp.status_code == 422


def test_create_comment_unknown_session_returns_404(authed_client):
    c = authed_client("readonly")
    resp = c.post("/api/comments", json={"sessionPk": "missing", "text": "hi"}, headers=ORIGIN)
    assert resp.status_code == 404


def test_delete_comment_by_author(authed_client, fake_db):
    _seed_session(fake_db)
    c = authed_client("readonly")
    created = c.post(
        "/api/comments", json={"sessionPk": "session1", "text": "mine"}, headers=ORIGIN
    ).json()

    resp = c.delete(f"/api/comments/{created['pk']}", headers=ORIGIN)
    assert resp.status_code == 204
    assert c.get("/api/reactions", headers=ORIGIN).json() == []


def test_delete_comment_by_other_user_returns_404(authed_client, fake_db):
    # A2: a non-owner gets a uniform 404 (not 403) so they can't distinguish
    # "comment exists" from "comment doesn't exist".
    _seed_session(fake_db)
    c = authed_client("readonly")
    created = c.post(
        "/api/comments", json={"sessionPk": "session1", "text": "mine"}, headers=ORIGIN
    ).json()

    other = authed_client("readonly")
    other.cookies.set("token", make_auth_cookie("readonly", sub="otheruser")["token"])
    resp = other.delete(f"/api/comments/{created['pk']}", headers=ORIGIN)
    assert resp.status_code == 404


def test_delete_comment_by_admin_allowed_for_other_users_comment(authed_client, fake_db):
    _seed_session(fake_db)
    author = authed_client("readonly")
    created = author.post(
        "/api/comments", json={"sessionPk": "session1", "text": "mine"}, headers=ORIGIN
    ).json()

    admin = authed_client("admin")
    admin.cookies.set("token", make_auth_cookie("admin", sub="otheradmin")["token"])
    resp = admin.delete(f"/api/comments/{created['pk']}", headers=ORIGIN)
    assert resp.status_code == 204


def test_delete_comment_unknown_id_returns_404(authed_client):
    c = authed_client("admin")
    resp = c.delete("/api/comments/does-not-exist", headers=ORIGIN)
    assert resp.status_code == 404


def test_delete_reaction_item_via_comments_route_returns_404(authed_client, fake_db):
    _seed_session(fake_db)
    c = authed_client("readonly")
    c.post("/api/reactions/toggle", json={"sessionPk": "session1", "emoji": "👍"}, headers=ORIGIN)
    reaction_pk = c.get("/api/reactions", headers=ORIGIN).json()[0]["pk"]

    resp = c.delete(f"/api/comments/{reaction_pk}", headers=ORIGIN)
    assert resp.status_code == 404
