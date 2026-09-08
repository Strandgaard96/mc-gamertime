from routes.results import detect_milestone


def _r(winner_id, player_ids, date="2024-01-01"):
    return {
        "winnerId": winner_id,
        "players": [{"playerId": pid} for pid in player_ids],
        "date": date,
    }


def test_first_win():
    results = [_r("alice", ["alice", "bob"])]
    assert detect_milestone("alice", "Alice", results) == "🎉 Alice got their first win!"


def test_streak_3():
    results = [
        _r("bob", ["alice", "bob"], "2024-01-01"),
        _r("alice", ["alice", "bob"], "2024-01-02"),
        _r("alice", ["alice", "bob"], "2024-01-03"),
        _r("alice", ["alice", "bob"], "2024-01-04"),
    ]
    assert detect_milestone("alice", "Alice", results) == "🔥 Alice is on a 3-game win streak!"


def test_streak_5():
    results = [
        _r("bob", ["alice", "bob"], "2024-01-01"),
        _r("alice", ["alice", "bob"], "2024-01-02"),
        _r("alice", ["alice", "bob"], "2024-01-03"),
        _r("alice", ["alice", "bob"], "2024-01-04"),
        _r("alice", ["alice", "bob"], "2024-01-05"),
        _r("alice", ["alice", "bob"], "2024-01-06"),
    ]
    assert detect_milestone("alice", "Alice", results) == "🔥 Alice is on fire — 5 in a row!"


def test_streak_10():
    results = [_r("alice", ["alice", "bob"], f"2024-01-{i:02d}") for i in range(1, 11)]
    assert (
        detect_milestone("alice", "Alice", results)
        == "👑 Alice is unstoppable — 10-game win streak!"
    )


def test_personal_best_broken():
    # Previous best streak = 2, current streak = 4 (not a milestone number)
    results = [
        _r("alice", ["alice", "bob"], "2024-01-01"),
        _r("alice", ["alice", "bob"], "2024-01-02"),
        _r("bob", ["alice", "bob"], "2024-01-03"),
        _r("alice", ["alice", "bob"], "2024-01-04"),
        _r("alice", ["alice", "bob"], "2024-01-05"),
        _r("alice", ["alice", "bob"], "2024-01-06"),
        _r("alice", ["alice", "bob"], "2024-01-07"),
    ]
    assert (
        detect_milestone("alice", "Alice", results)
        == "⚡ Alice just broke their personal best streak!"
    )


def test_no_milestone_low_streak():
    # Streak of 2 — below threshold, not first win
    results = [
        _r("bob", ["alice", "bob"], "2024-01-01"),
        _r("alice", ["alice", "bob"], "2024-01-02"),
        _r("alice", ["alice", "bob"], "2024-01-03"),
    ]
    assert detect_milestone("alice", "Alice", results) is None


def test_no_milestone_streak_broken():
    # Had streak of 3 before, now streak of 1 after a loss
    results = [
        _r("alice", ["alice", "bob"], "2024-01-01"),
        _r("alice", ["alice", "bob"], "2024-01-02"),
        _r("alice", ["alice", "bob"], "2024-01-03"),
        _r("bob", ["alice", "bob"], "2024-01-04"),
        _r("alice", ["alice", "bob"], "2024-01-05"),
    ]
    assert detect_milestone("alice", "Alice", results) is None


def test_no_milestone_not_winner():
    results = [_r("bob", ["alice", "bob"])]
    assert detect_milestone("alice", "Alice", results) is None


def test_returns_none_for_empty_winner():
    assert detect_milestone("", "Alice", []) is None
