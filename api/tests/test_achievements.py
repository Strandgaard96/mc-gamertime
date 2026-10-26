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
        "explorer_10",
        "heavyweight",
        "party_winner",
        "harkonnen_5",
        "giant_slayer",
        "comeback",
        "polymath",
        "specialist",
        "games_50",
        "marathon",
        "crowd_pleaser",
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


def _slayer(player_id: str, results: list[dict]) -> str | None:
    by_id = {a["id"]: a for a in compute_achievements(player_id, results, {})}
    return by_id["giant_slayer"]["earnedAt"]


A, B, C, D = ("p1", "Alice"), ("p2", "Bob"), ("p3", "Carol"), ("p4", "Dave")
# Alice beats Bob twice -> Alice is sole #1 going into 2026-01-03.
LEAD = [_r("p1", [A, B], "2026-01-01"), _r("p1", [A, B], "2026-01-02")]


def test_giant_slayer_earned_when_beating_the_leader():
    rs = [*LEAD, _r("p3", [C, A], "2026-01-03")]
    assert _slayer("p3", rs) == "2026-01-03"


def test_giant_slayer_not_when_leader_absent():
    rs = [*LEAD, _r("p3", [C, B], "2026-01-03")]
    assert _slayer("p3", rs) is None


def test_giant_slayer_not_when_player_is_the_leader():
    rs = [*LEAD, _r("p1", [A, C], "2026-01-03")]
    assert _slayer("p1", rs) is None


def test_giant_slayer_not_when_leader_won():
    rs = [*LEAD, _r("p1", [A, C], "2026-01-03")]
    assert _slayer("p3", rs) is None


def test_giant_slayer_not_when_top_is_tied():
    rs = [
        _r("p1", [A, B], "2026-01-01"),
        _r("p3", [C, D], "2026-01-02"),  # Alice and Carol both 1016
        _r("p2", [B, A], "2026-01-03"),
    ]
    assert _slayer("p2", rs) is None


def test_giant_slayer_accepts_precomputed_leader_map():
    rs = [*LEAD, _r("p3", [C, B], "2026-01-03")]
    # Force Bob as "leader" via the explicit map: Carol beat him -> earned.
    forced: dict[str, str | None] = {"result-2026-01-03": "p2"}
    by_id = {a["id"]: a for a in compute_achievements("p3", rs, {}, leader_before=forced)}
    assert by_id["giant_slayer"]["earnedAt"] == "2026-01-03"


def _earned(player_id: str, results: list[dict], games_by_id: dict | None = None) -> dict:
    return {
        a["id"]: a["earnedAt"] for a in compute_achievements(player_id, results, games_by_id or {})
    }


def _day(i: int) -> str:
    return f"2026-{(i // 28) + 1:02d}-{(i % 28) + 1:02d}"


def test_comeback_earned_on_win_after_five_losses():
    results = [_r("p2", PLAYERS, _day(i)) for i in range(5)] + [_r("p1", PLAYERS, _day(5))]
    assert _earned("p1", results)["comeback"] == _day(5)


def test_comeback_earned_after_longer_losing_streak():
    results = [_r("p2", PLAYERS, _day(i)) for i in range(7)] + [_r("p1", PLAYERS, _day(7))]
    assert _earned("p1", results)["comeback"] == _day(7)


def test_comeback_not_earned_after_four_losses():
    results = [_r("p2", PLAYERS, _day(i)) for i in range(4)] + [_r("p1", PLAYERS, _day(4))]
    assert _earned("p1", results)["comeback"] is None


def test_comeback_not_earned_when_streak_broken_by_win():
    results = (
        [_r("p2", PLAYERS, _day(i)) for i in range(3)]
        + [_r("p1", PLAYERS, _day(3))]
        + [_r("p2", PLAYERS, _day(i)) for i in range(4, 6)]
        + [_r("p1", PLAYERS, _day(6))]
    )
    assert _earned("p1", results)["comeback"] is None


def test_comeback_not_earned_while_still_losing():
    results = [_r("p2", PLAYERS, _day(i)) for i in range(6)]
    assert _earned("p1", results)["comeback"] is None


def test_polymath_earned_on_tenth_distinct_game_won():
    results = [_r("p1", PLAYERS, _day(i), game_id=f"game-{i}") for i in range(10)]
    assert _earned("p1", results)["polymath"] == _day(9)


def test_polymath_ignores_distinct_games_lost():
    results = [_r("p1", PLAYERS, _day(i), game_id=f"game-{i}") for i in range(9)] + [
        _r("p2", PLAYERS, _day(9), game_id="game-9")
    ]
    assert _earned("p1", results)["polymath"] is None


def test_specialist_earned_on_fifth_win_of_same_game():
    results = [_r("p1", PLAYERS, _day(i), game_id="game-x") for i in range(5)]
    assert _earned("p1", results)["specialist"] == _day(4)


def test_specialist_not_earned_when_wins_spread_across_games():
    results = [_r("p1", PLAYERS, _day(i), game_id=f"game-{i % 2}") for i in range(5)]
    assert _earned("p1", results)["specialist"] is None


def test_games_50_earned_on_fiftieth_game():
    results = [_r("p2", PLAYERS, _day(i)) for i in range(50)]
    earned = _earned("p1", results)
    assert earned["games_50"] == _day(49)


def test_games_50_not_earned_at_49():
    results = [_r("p2", PLAYERS, _day(i)) for i in range(49)]
    assert _earned("p1", results)["games_50"] is None


def test_marathon_earned_on_win_of_long_game():
    games = {"game-long": {**_g("game-long"), "playTime": 120}}
    results = [_r("p1", PLAYERS, _day(0), game_id="game-long")]
    assert _earned("p1", results, games)["marathon"] == _day(0)


def test_marathon_not_earned_for_short_or_unknown_play_time():
    games = {"game-short": {**_g("game-short"), "playTime": 90}, "game-unknown": _g("game-unknown")}
    results = [
        _r("p1", PLAYERS, _day(0), game_id="game-short"),
        _r("p1", PLAYERS, _day(1), game_id="game-unknown"),
    ]
    assert _earned("p1", results, games)["marathon"] is None


def test_marathon_not_earned_on_loss():
    games = {"game-long": {**_g("game-long"), "playTime": 180}}
    results = [_r("p2", PLAYERS, _day(0), game_id="game-long")]
    assert _earned("p1", results, games)["marathon"] is None


FIVE = [A, B, C, D, ("p5", "Eve")]


def test_crowd_pleaser_earned_on_win_with_five_players():
    results = [_r("p1", FIVE, _day(0))]
    assert _earned("p1", results)["crowd_pleaser"] == _day(0)


def test_crowd_pleaser_not_earned_with_four_players():
    results = [_r("p1", FIVE[:4], _day(0))]
    assert _earned("p1", results)["crowd_pleaser"] is None


def test_crowd_pleaser_not_earned_on_loss():
    results = [_r("p2", FIVE, _day(0))]
    assert _earned("p1", results)["crowd_pleaser"] is None
