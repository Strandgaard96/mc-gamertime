from lib.db.notifications import list_notifications_for_player, put_notification


def test_list_notifications_for_player_filters_and_sorts(fake_db):
    put_notification(
        {
            "pk": "n1",
            "playerId": "alice",
            "achievementId": "first_win",
            "label": "First Blood",
            "icon": "🏆",
            "description": "Won your first game",
            "gameId": "01GAME",
            "gameName": "Catan",
            "resultId": "01RESULT-1",
            "createdAt": "2026-01-01T00:00:00+00:00",
        }
    )
    put_notification(
        {
            "pk": "n2",
            "playerId": "alice",
            "achievementId": "games_10",
            "label": "Regular",
            "icon": "🎲",
            "description": "Played 10 games",
            "gameId": "01GAME",
            "gameName": "Catan",
            "resultId": "01RESULT-10",
            "createdAt": "2026-02-01T00:00:00+00:00",
        }
    )
    put_notification(
        {
            "pk": "n3",
            "playerId": "bob",
            "achievementId": "first_win",
            "label": "First Blood",
            "icon": "🏆",
            "description": "Won your first game",
            "gameId": "01GAME",
            "gameName": "Catan",
            "resultId": "01RESULT-2",
            "createdAt": "2026-01-02T00:00:00+00:00",
        }
    )

    items = list_notifications_for_player("alice")

    assert [n["pk"] for n in items] == ["n2", "n1"]  # newest first
