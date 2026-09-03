from lib.achievements.engine import AchievementContext
from lib.achievements.rules import (
    all_of,
    counter_threshold,
    distinct_count_threshold,
    game_has_tag,
    game_name_is,
    game_weight_at_least,
    is_win,
    score_at_least,
    streak_threshold,
    variable_equals,
)


def _result(
    winner_id="p1",
    date="2026-01-01",
    game_id="game-1",
    game_name="Catan",
    players=None,
    score=None,
    variables=None,
):
    if players is None:
        entry = {"playerId": "p1", "playerName": "Alice"}
        if score is not None:
            entry["score"] = score
        if variables is not None:
            entry["variables"] = variables
        players = [entry, {"playerId": "p2", "playerName": "Bob"}]
    return {
        "pk": f"result-{date}",
        "gameId": game_id,
        "gameName": game_name,
        "date": date,
        "players": players,
        "winnerId": winner_id,
        "winnerName": "Alice" if winner_id == "p1" else "Bob",
        "createdAt": f"{date}T00:00:00Z",
    }


# --- AchievementContext ---


def test_my_entry_finds_player():
    ctx = AchievementContext("p1", {})
    r = _result()
    assert ctx.my_entry(r)["playerId"] == "p1"


def test_my_entry_returns_none_when_absent():
    ctx = AchievementContext("p3", {})
    r = _result()
    assert ctx.my_entry(r) is None


def test_game_returns_empty_dict_when_gameid_missing_from_map():
    ctx = AchievementContext("p1", {})
    r = _result(game_id="game-1")
    assert ctx.game(r) == {}


def test_game_returns_mapped_game():
    ctx = AchievementContext("p1", {"game-1": {"name": "Catan", "weight": 2.3}})
    r = _result(game_id="game-1")
    assert ctx.game(r)["weight"] == 2.3


# --- predicates ---


def test_is_win_true_for_winner():
    ctx = AchievementContext("p1", {})
    assert is_win(ctx, _result(winner_id="p1")) is True


def test_is_win_false_for_loser():
    ctx = AchievementContext("p1", {})
    assert is_win(ctx, _result(winner_id="p2")) is False


def test_score_at_least_true_when_score_meets_threshold():
    ctx = AchievementContext("p1", {})
    r = _result(score=10)
    assert score_at_least(10)(ctx, r) is True


def test_score_at_least_false_when_score_below_threshold():
    ctx = AchievementContext("p1", {})
    r = _result(score=9.5)
    assert score_at_least(10)(ctx, r) is False


def test_score_at_least_false_when_no_score():
    ctx = AchievementContext("p1", {})
    r = _result()
    assert score_at_least(10)(ctx, r) is False


def test_game_weight_at_least_true_when_weight_meets_threshold():
    ctx = AchievementContext("p1", {"game-1": {"weight": 4.5}})
    assert game_weight_at_least(4.0)(ctx, _result()) is True


def test_game_weight_at_least_false_when_weight_missing():
    ctx = AchievementContext("p1", {"game-1": {}})
    assert game_weight_at_least(4.0)(ctx, _result()) is False


def test_game_has_tag_case_insensitive():
    ctx = AchievementContext("p1", {"game-1": {"tags": ["Party", "Strategy"]}})
    assert game_has_tag("party")(ctx, _result()) is True


def test_game_has_tag_false_when_absent():
    ctx = AchievementContext("p1", {"game-1": {"tags": ["Strategy"]}})
    assert game_has_tag("party")(ctx, _result()) is False


def test_game_name_is_case_insensitive():
    r = _result(game_name="Dune: Imperium")
    ctx = AchievementContext("p1", {})
    assert game_name_is("dune: imperium")(ctx, r) is True


def test_variable_equals_matches_by_label_and_value():
    ctx = AchievementContext(
        "p1",
        {
            "game-1": {
                "playerVariables": [
                    {"id": "faction", "label": "Faction", "options": ["Atreides", "Harkonnen"]},
                ]
            }
        },
    )
    r = _result(variables={"faction": "Harkonnen"})
    assert variable_equals("Faction", "Harkonnen")(ctx, r) is True


def test_variable_equals_false_when_value_differs():
    ctx = AchievementContext(
        "p1",
        {
            "game-1": {
                "playerVariables": [
                    {"id": "faction", "label": "Faction", "options": ["Atreides", "Harkonnen"]},
                ]
            }
        },
    )
    r = _result(variables={"faction": "Atreides"})
    assert variable_equals("Faction", "Harkonnen")(ctx, r) is False


def test_variable_equals_resolves_current_id_after_label_rename():
    # Variable id is "faction-2" now (e.g. after a relabel), but label is still "Faction"
    ctx = AchievementContext(
        "p1",
        {
            "game-1": {
                "playerVariables": [
                    {"id": "faction-2", "label": "Faction", "options": ["Atreides", "Harkonnen"]},
                ]
            }
        },
    )
    r = _result(variables={"faction-2": "Harkonnen"})
    assert variable_equals("Faction", "Harkonnen")(ctx, r) is True


def test_variable_equals_false_when_variable_not_on_game():
    ctx = AchievementContext("p1", {"game-1": {"playerVariables": []}})
    r = _result(variables={"faction": "Harkonnen"})
    assert variable_equals("Faction", "Harkonnen")(ctx, r) is False


def test_all_of_requires_every_predicate():
    ctx = AchievementContext("p1", {"game-1": {"weight": 4.5}})
    pred = all_of(is_win, game_weight_at_least(4.0))
    assert pred(ctx, _result(winner_id="p1")) is True
    assert pred(ctx, _result(winner_id="p2")) is False


# --- rule factories ---


def test_counter_threshold_returns_date_when_count_reached():
    ctx = AchievementContext("p1", {})
    rule = counter_threshold(is_win, 2)
    results = [
        _result(winner_id="p1", date="2026-01-01"),
        _result(winner_id="p1", date="2026-01-02"),
    ]
    assert rule(ctx, results) == "2026-01-02"


def test_counter_threshold_returns_none_when_not_reached():
    ctx = AchievementContext("p1", {})
    rule = counter_threshold(is_win, 3)
    results = [
        _result(winner_id="p1", date="2026-01-01"),
        _result(winner_id="p1", date="2026-01-02"),
    ]
    assert rule(ctx, results) is None


def test_streak_threshold_resets_on_break():
    ctx = AchievementContext("p1", {})
    rule = streak_threshold(is_win, 2)
    results = [
        _result(winner_id="p1", date="2026-01-01"),
        _result(winner_id="p2", date="2026-01-02"),
        _result(winner_id="p1", date="2026-01-03"),
        _result(winner_id="p1", date="2026-01-04"),
    ]
    assert rule(ctx, results) == "2026-01-04"


def test_distinct_count_threshold_counts_unique_keys():
    ctx = AchievementContext("p1", {})
    rule = distinct_count_threshold(lambda ctx, r: r["gameId"], 2)
    results = [
        _result(date="2026-01-01", game_id="game-1"),
        _result(date="2026-01-02", game_id="game-1"),
        _result(date="2026-01-03", game_id="game-2"),
    ]
    assert rule(ctx, results) == "2026-01-03"
