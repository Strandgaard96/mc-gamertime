"""Calendar-quarter seasons, computed on the fly from results.

Nothing is persisted: a season's standings and champion are a pure function of
the results whose `date` (game date, YYYY-MM-DD) falls inside the quarter. That
means backdating/editing/deleting a result can change a finished season's
champion — intended, the results stay the single source of truth.
"""

from __future__ import annotations

from datetime import UTC, date, datetime, timedelta

from lib.stats import compute_stats

SEASON_PATTERN = r"^\d{4}-Q[1-4]$"
MIN_CHAMPION_GAMES = 5


def today_utc() -> date:
    return datetime.now(UTC).date()


def season_of(d: str) -> str:
    year, month = int(d[:4]), int(d[5:7])
    return f"{year}-Q{(month - 1) // 3 + 1}"


def season_label(season_id: str) -> str:
    year, quarter = season_id.split("-")
    return f"{quarter} {year}"


def _last_day(season_id: str) -> date:
    year, quarter = int(season_id[:4]), int(season_id[-1])
    if quarter == 4:
        return date(year, 12, 31)
    return date(year, quarter * 3 + 1, 1) - timedelta(days=1)


def is_finished(season_id: str, today: date) -> bool:
    return today > _last_day(season_id)


def results_in_season(results: list[dict], season_id: str) -> list[dict]:
    return [r for r in results if season_of(r["date"]) == season_id]


def _rank_key(entry: dict) -> tuple:
    return (entry["rating"], entry["wins"], entry["winRate"])


def season_champion(season_results: list[dict]) -> dict | None:
    """Top of the season leaderboard among players with >= MIN_CHAMPION_GAMES
    games; None if nobody qualifies or the top two tie on every sort key."""
    board = [
        e for e in compute_stats(season_results)["leaderboard"] if e["played"] >= MIN_CHAMPION_GAMES
    ]
    if not board:
        return None
    top = board[0]
    if len(board) > 1 and _rank_key(board[1]) == _rank_key(top):
        return None
    return {"playerId": top["playerId"], "name": top["name"]}


def list_seasons(results: list[dict], today: date) -> list[dict]:
    """Every quarter with >= 1 result plus the current quarter, newest first."""
    ids = {season_of(r["date"]) for r in results} | {season_of(today.isoformat())}
    seasons = []
    for season_id in sorted(ids, reverse=True):
        finished = is_finished(season_id, today)
        champion = season_champion(results_in_season(results, season_id)) if finished else None
        seasons.append(
            {
                "id": season_id,
                "label": season_label(season_id),
                "finished": finished,
                "champion": champion,
            }
        )
    return seasons


def player_season_titles(results: list[dict], player_id: str, today: date) -> list[dict]:
    return [
        {"id": s["id"], "label": s["label"]}
        for s in list_seasons(results, today)
        if s["champion"] and s["champion"]["playerId"] == player_id
    ]
