from lib.elo import compute_elo


def _result(
    winner_id: str,
    players: list[str],
    date: str = "2026-01-01",
    created_at: str = "2026-01-01T00:00:00Z",
) -> dict:
    return {
        "gameId": "game-1",
        "gameName": "Catan",
        "date": date,
        "players": [{"playerId": pid, "playerName": pid.title()} for pid in players],
        "winnerId": winner_id,
        "createdAt": created_at,
    }


def test_empty_results_returns_empty_ratings():
    assert compute_elo([]) == {}


def test_two_player_game_winner_gains_what_loser_loses():
    ratings = compute_elo([_result("p1", ["p1", "p2"])])
    # Both start at 1000, expected = 0.5, delta = 32 * 0.5 = 16
    assert ratings == {"p1": 1016, "p2": 984}


def test_upset_win_gains_more_than_expected_win():
    # p1 beats p2 twice, building a rating lead
    history = [
        _result("p1", ["p1", "p2"], date="2026-01-01"),
        _result("p1", ["p1", "p2"], date="2026-01-02"),
    ]
    before = compute_elo(history)
    after = compute_elo(history + [_result("p2", ["p1", "p2"], date="2026-01-03")])
    upset_gain = after["p2"] - before["p2"]
    # Beating a higher-rated player must pay more than the even-match 16
    assert upset_gain > 16


def test_four_player_game_splits_k_across_opponents():
    ratings = compute_elo([_result("p1", ["p1", "p2", "p3", "p4"])])
    # 3 duels at K/3: winner gains 3 * (32/3) * 0.5 = 16
    assert ratings["p1"] == 1016
    # Each loser drops (32/3) * 0.5 = 5.33 -> 994.67 rounds to 995
    assert ratings["p2"] == ratings["p3"] == ratings["p4"] == 995


def test_replay_order_is_by_date_then_created_at_not_list_order():
    a = _result("p1", ["p1", "p2"], date="2026-01-01", created_at="2026-01-01T10:00:00Z")
    b = _result("p2", ["p1", "p2"], date="2026-01-01", created_at="2026-01-01T11:00:00Z")
    c = _result("p1", ["p1", "p2"], date="2026-01-02", created_at="2026-01-02T09:00:00Z")
    assert compute_elo([a, b, c]) == compute_elo([c, b, a])


def test_single_player_result_skipped():
    ratings = compute_elo([_result("p1", ["p1"])])
    assert ratings == {}


def test_winner_not_in_players_skipped():
    bad = _result("ghost", ["p1", "p2"])
    assert compute_elo([bad]) == {}
