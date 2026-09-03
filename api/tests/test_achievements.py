from lib.achievements import ACHIEVEMENT_DEFS, compute_achievements

PLAYERS = [("p1", "Alice"), ("p2", "Bob")]


def _r(
    winner_id: str,
    players: list[tuple[str, str]],
    date: str,
    game_id: str = "game-1",
    game_name: str = "Catan",
) -> dict:
    return {
        "pk": f"result-{date}",
        "gameId": game_id,
        "gameName": game_name,
        "date": date,
        "players": [{"playerId": pid, "playerName": name} for pid, name in players],
        "winnerId": winner_id,
        "winnerName": dict(players).get(winner_id, ""),
        "createdAt": f"{date}T00:00:00Z",
    }


def _g(pk: str, **kwargs) -> dict:
    game = {
        "pk": pk,
        "name": kwargs.get("name", pk),
        "tags": kwargs.get("tags", []),
        "playerVariables": kwargs.get("playerVariables", []),
    }
    if "weight" in kwargs:
        game["weight"] = kwargs["weight"]
    return game


def test_all_achievement_ids_present_in_empty_results():
    achievements = compute_achievements("p1", [], {})
    ids = {a["id"] for a in achievements}
    expected = {
        "first_win",
        "streak_3",
        "streak_5",
        "games_10",
        "games_25",
        "wins_10",
        "wins_25",
        "dominant",
        "perfect_10",
        "explorer_10",
        "heavyweight",
        "party_winner",
        "harkonnen_5",
    }
    assert ids == expected


def test_no_results_all_unearned():
    achievements = compute_achievements("p1", [], {})
    assert all(a["earnedAt"] is None for a in achievements)


def test_results_for_other_player_ignored():
    results = [_r("p2", PLAYERS, "2026-01-01")]
    achievements = {a["id"]: a for a in compute_achievements("p1", results, {})}
    assert achievements["first_win"]["earnedAt"] is None
    assert achievements["games_10"]["earnedAt"] is None


def test_first_win_earned_on_first_win():
    results = [_r("p1", PLAYERS, "2026-01-01")]
    achievements = {a["id"]: a for a in compute_achievements("p1", results, {})}
    assert achievements["first_win"]["earnedAt"] == "2026-01-01"


def test_first_win_not_earned_on_loss():
    results = [_r("p2", PLAYERS, "2026-01-01")]
    achievements = {a["id"]: a for a in compute_achievements("p1", results, {})}
    assert achievements["first_win"]["earnedAt"] is None


def test_streak_3_earned_on_third_consecutive_win():
    results = [
        _r("p1", PLAYERS, "2026-01-01"),
        _r("p1", PLAYERS, "2026-01-02"),
        _r("p1", PLAYERS, "2026-01-03"),
    ]
    achievements = {a["id"]: a for a in compute_achievements("p1", results, {})}
    assert achievements["streak_3"]["earnedAt"] == "2026-01-03"
    assert achievements["streak_5"]["earnedAt"] is None


def test_streak_5_earned_on_fifth_consecutive_win():
    results = [_r("p1", PLAYERS, f"2026-01-0{i + 1}") for i in range(5)]
    achievements = {a["id"]: a for a in compute_achievements("p1", results, {})}
    assert achievements["streak_5"]["earnedAt"] == "2026-01-05"


def test_streak_achievement_permanent_after_loss():
    results = [
        _r("p1", PLAYERS, "2026-01-01"),
        _r("p1", PLAYERS, "2026-01-02"),
        _r("p1", PLAYERS, "2026-01-03"),
        _r("p2", PLAYERS, "2026-01-04"),
    ]
    achievements = {a["id"]: a for a in compute_achievements("p1", results, {})}
    assert achievements["streak_3"]["earnedAt"] == "2026-01-03"


def test_streak_earned_at_is_date_of_completing_win_not_later():
    results = [_r("p1", PLAYERS, f"2026-01-0{i + 1}") for i in range(5)]
    achievements = {a["id"]: a for a in compute_achievements("p1", results, {})}
    assert achievements["streak_3"]["earnedAt"] == "2026-01-03"
    assert achievements["streak_5"]["earnedAt"] == "2026-01-05"


def test_games_10_earned_on_tenth_game():
    results = [_r("p2", PLAYERS, f"2026-01-{i + 1:02d}") for i in range(10)]
    achievements = {a["id"]: a for a in compute_achievements("p1", results, {})}
    assert achievements["games_10"]["earnedAt"] == "2026-01-10"
    assert achievements["games_25"]["earnedAt"] is None


def test_games_25_earned_on_twenty_fifth_game():
    results = [_r("p2", PLAYERS, f"2026-{(i // 28) + 1:02d}-{(i % 28) + 1:02d}") for i in range(25)]
    achievements = {a["id"]: a for a in compute_achievements("p1", results, {})}
    assert achievements["games_25"]["earnedAt"] is not None


def test_wins_10_earned_on_tenth_win():
    results = [_r("p1", PLAYERS, f"2026-01-{i + 1:02d}") for i in range(10)]
    achievements = {a["id"]: a for a in compute_achievements("p1", results, {})}
    assert achievements["wins_10"]["earnedAt"] == "2026-01-10"
    assert achievements["wins_25"]["earnedAt"] is None


def test_dominant_earned_when_winrate_first_hits_70_with_10_played():
    results = [_r("p1", PLAYERS, f"2026-01-{i + 1:02d}") for i in range(7)] + [
        _r("p2", PLAYERS, f"2026-01-{i + 8:02d}") for i in range(3)
    ]
    achievements = {a["id"]: a for a in compute_achievements("p1", results, {})}
    assert achievements["dominant"]["earnedAt"] == "2026-01-10"


def test_dominant_not_earned_below_10_games():
    results = [_r("p1", PLAYERS, f"2026-01-0{i + 1}") for i in range(3)]
    achievements = {a["id"]: a for a in compute_achievements("p1", results, {})}
    assert achievements["dominant"]["earnedAt"] is None


def test_achievement_defs_have_required_fields():
    for d in ACHIEVEMENT_DEFS:
        assert "id" in d
        assert "label" in d
        assert "description" in d
        assert "icon" in d


def test_perfect_10_earned_on_score_of_ten():
    results = [
        {
            "pk": "01A",
            "gameId": "game-1",
            "gameName": "Catan",
            "date": "2026-01-01",
            "winnerId": "bob",
            "winnerName": "Bob",
            "players": [{"playerId": "alice", "playerName": "Alice", "score": 7}],
        },
        {
            "pk": "01B",
            "gameId": "game-1",
            "gameName": "Catan",
            "date": "2026-02-01",
            "winnerId": "alice",
            "winnerName": "Alice",
            "players": [{"playerId": "alice", "playerName": "Alice", "score": 10}],
        },
    ]
    achievements = {a["id"]: a for a in compute_achievements("alice", results, {})}
    assert achievements["perfect_10"]["earnedAt"] == "2026-02-01"


def test_perfect_10_not_earned_without_ten():
    results = [
        {
            "pk": "01A",
            "gameId": "game-1",
            "gameName": "Catan",
            "date": "2026-01-01",
            "winnerId": "alice",
            "winnerName": "Alice",
            "players": [{"playerId": "alice", "playerName": "Alice", "score": 9.5}],
        },
    ]
    achievements = {a["id"]: a for a in compute_achievements("alice", results, {})}
    assert achievements["perfect_10"]["earnedAt"] is None


def test_explorer_10_earned_on_tenth_distinct_game():
    results = [
        _r(
            "p2",
            PLAYERS,
            f"2026-01-{i + 1:02d}",
            game_id=f"game-{i + 1}",
            game_name=f"Game {i + 1}",
        )
        for i in range(10)
    ]
    achievements = {a["id"]: a for a in compute_achievements("p1", results, {})}
    assert achievements["explorer_10"]["earnedAt"] == "2026-01-10"


def test_explorer_10_not_earned_when_replaying_same_game():
    results = [_r("p2", PLAYERS, f"2026-01-{i + 1:02d}") for i in range(10)]
    achievements = {a["id"]: a for a in compute_achievements("p1", results, {})}
    assert achievements["explorer_10"]["earnedAt"] is None


def test_heavyweight_earned_on_win_with_heavy_game():
    games_by_id = {"game-heavy": _g("game-heavy", name="Gloomhaven", weight=4.5)}
    results = [_r("p1", PLAYERS, "2026-01-01", game_id="game-heavy", game_name="Gloomhaven")]
    achievements = {a["id"]: a for a in compute_achievements("p1", results, games_by_id)}
    assert achievements["heavyweight"]["earnedAt"] == "2026-01-01"


def test_heavyweight_not_earned_when_loss():
    games_by_id = {"game-heavy": _g("game-heavy", name="Gloomhaven", weight=4.5)}
    results = [_r("p2", PLAYERS, "2026-01-01", game_id="game-heavy", game_name="Gloomhaven")]
    achievements = {a["id"]: a for a in compute_achievements("p1", results, games_by_id)}
    assert achievements["heavyweight"]["earnedAt"] is None


def test_heavyweight_not_earned_below_weight_threshold():
    games_by_id = {"game-1": _g("game-1", name="Catan", weight=2.3)}
    results = [_r("p1", PLAYERS, "2026-01-01")]
    achievements = {a["id"]: a for a in compute_achievements("p1", results, games_by_id)}
    assert achievements["heavyweight"]["earnedAt"] is None


def test_party_winner_earned_on_win_with_tagged_game():
    games_by_id = {"game-party": _g("game-party", name="Codenames", tags=["Party", "Word"])}
    results = [_r("p1", PLAYERS, "2026-01-01", game_id="game-party", game_name="Codenames")]
    achievements = {a["id"]: a for a in compute_achievements("p1", results, games_by_id)}
    assert achievements["party_winner"]["earnedAt"] == "2026-01-01"


def test_party_winner_not_earned_without_tag():
    games_by_id = {"game-1": _g("game-1", name="Catan", tags=[])}
    results = [_r("p1", PLAYERS, "2026-01-01")]
    achievements = {a["id"]: a for a in compute_achievements("p1", results, games_by_id)}
    assert achievements["party_winner"]["earnedAt"] is None


def _dune_result(winner_id: str, date: str, faction: str) -> dict:
    return {
        "pk": f"result-{date}",
        "gameId": "game-dune",
        "gameName": "Dune: Imperium",
        "date": date,
        "players": [
            {"playerId": "p1", "playerName": "Alice", "variables": {"faction": faction}},
            {"playerId": "p2", "playerName": "Bob", "variables": {"faction": "Atreides"}},
        ],
        "winnerId": winner_id,
        "winnerName": "Alice" if winner_id == "p1" else "Bob",
        "createdAt": f"{date}T00:00:00Z",
    }


def test_harkonnen_5_earned_on_fifth_win_as_harkonnen():
    games_by_id = {
        "game-dune": _g(
            "game-dune",
            name="Dune: Imperium",
            playerVariables=[
                {
                    "id": "faction",
                    "label": "Faction",
                    "options": ["Atreides", "Harkonnen", "Fremen"],
                }
            ],
        )
    }
    results = [_dune_result("p1", f"2026-01-{i + 1:02d}", "Harkonnen") for i in range(5)]
    achievements = {a["id"]: a for a in compute_achievements("p1", results, games_by_id)}
    assert achievements["harkonnen_5"]["earnedAt"] == "2026-01-05"


def test_harkonnen_5_not_earned_with_different_faction():
    games_by_id = {
        "game-dune": _g(
            "game-dune",
            name="Dune: Imperium",
            playerVariables=[
                {
                    "id": "faction",
                    "label": "Faction",
                    "options": ["Atreides", "Harkonnen", "Fremen"],
                }
            ],
        )
    }
    results = [_dune_result("p1", f"2026-01-{i + 1:02d}", "Atreides") for i in range(5)]
    achievements = {a["id"]: a for a in compute_achievements("p1", results, games_by_id)}
    assert achievements["harkonnen_5"]["earnedAt"] is None
