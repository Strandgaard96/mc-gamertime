from datetime import date

from lib.seasons import (
    MIN_CHAMPION_GAMES,
    is_finished,
    list_seasons,
    player_season_titles,
    results_in_season,
    season_champion,
    season_label,
    season_of,
)


def _r(pk: str, date_: str, winner: str, players: list[str]) -> dict:
    return {
        "pk": pk,
        "gameId": "g1",
        "gameName": "Catan",
        "date": date_,
        "players": [{"playerId": p, "playerName": p.title()} for p in players],
        "winnerId": winner,
        "winnerName": winner.title(),
        "createdAt": f"{date_}T00:00:00Z",
    }


def _games(n: int, winner: str, players: list[str], month: str = "2026-04") -> list[dict]:
    return [_r(f"{winner}-{month}-{i}", f"{month}-{i + 1:02d}", winner, players) for i in range(n)]


def test_season_of_quarter_boundaries():
    assert season_of("2026-03-31") == "2026-Q1"
    assert season_of("2026-04-01") == "2026-Q2"
    assert season_of("2026-12-31") == "2026-Q4"
    assert season_of("2027-01-01") == "2027-Q1"


def test_season_label():
    assert season_label("2026-Q3") == "Q3 2026"


def test_is_finished_only_after_last_day():
    assert not is_finished("2026-Q3", date(2026, 9, 30))
    assert is_finished("2026-Q3", date(2026, 10, 1))
    assert not is_finished("2026-Q4", date(2026, 12, 31))
    assert is_finished("2026-Q4", date(2027, 1, 1))


def test_results_in_season_filters_by_game_date():
    rs = [_r("a", "2026-03-31", "x", ["x", "y"]), _r("b", "2026-04-01", "x", ["x", "y"])]
    assert [r["pk"] for r in results_in_season(rs, "2026-Q2")] == ["b"]


def test_champion_requires_min_games():
    # bob: 4/4 wins -> highest rating but one game short of qualifying.
    # carol: 3 wins + 2 losses vs dave -> qualifies (5 games), rated above dave.
    rs = (
        _games(MIN_CHAMPION_GAMES - 1, "bob", ["bob", "alice"], "2026-04")
        + _games(3, "carol", ["carol", "dave"], "2026-05")
        + _games(2, "dave", ["carol", "dave"], "2026-06")
    )
    from lib.stats import compute_stats

    assert compute_stats(rs)["leaderboard"][0]["playerId"] == "bob"  # filter is what excludes him
    assert season_champion(rs) == {"playerId": "carol", "name": "Carol"}


def test_champion_none_when_nobody_qualifies():
    assert season_champion(_games(MIN_CHAMPION_GAMES - 1, "bob", ["bob", "alice"])) is None


def test_champion_none_on_full_tie():
    # Two disjoint pairs with identical histories: winners tie on rating, wins, winRate.
    rs = _games(5, "a", ["a", "b"], "2026-04") + _games(5, "c", ["c", "d"], "2026-05")
    assert season_champion(rs) is None


def test_list_seasons_always_includes_current_quarter():
    seasons = list_seasons([], date(2026, 10, 7))
    assert seasons == [{"id": "2026-Q4", "label": "Q4 2026", "finished": False, "champion": None}]


def test_list_seasons_newest_first_and_champion_only_when_finished():
    rs = _games(5, "carol", ["carol", "dave"], "2026-04") + _games(
        5, "carol", ["carol", "dave"], "2026-10"
    )
    seasons = list_seasons(rs, date(2026, 10, 7))
    assert [s["id"] for s in seasons] == ["2026-Q4", "2026-Q2"]
    assert seasons[0]["champion"] is None
    assert seasons[1]["finished"] is True
    assert seasons[1]["champion"] == {"playerId": "carol", "name": "Carol"}


def test_player_season_titles():
    rs = _games(5, "carol", ["carol", "dave"], "2026-04")
    today = date(2026, 10, 7)
    assert player_season_titles(rs, "carol", today) == [{"id": "2026-Q2", "label": "Q2 2026"}]
    assert player_season_titles(rs, "dave", today) == []
