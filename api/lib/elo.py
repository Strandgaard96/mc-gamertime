from __future__ import annotations

from collections.abc import Iterator

START_RATING = 1000.0
K = 32.0


def _ordered(results: list[dict]) -> list[dict]:
    return sorted(results, key=lambda r: (r["date"], r.get("createdAt", "")))


def _apply(ratings: dict[str, float], r: dict) -> None:
    """Winner duels each other participant pairwise. Unrated results are no-ops."""
    player_ids = [p["playerId"] for p in r.get("players", []) if p.get("playerId")]
    winner_id = r.get("winnerId")
    if not winner_id or len(player_ids) < 2 or winner_id not in player_ids:
        return

    for pid in player_ids:
        ratings.setdefault(pid, START_RATING)

    opponents = [pid for pid in player_ids if pid != winner_id]
    k_per_duel = K / len(opponents)
    pre = dict(ratings)

    winner_gain = 0.0
    for opp in opponents:
        expected = 1 / (1 + 10 ** ((pre[opp] - pre[winner_id]) / 400))
        delta = k_per_duel * (1 - expected)
        ratings[opp] -= delta
        winner_gain += delta
    ratings[winner_id] += winner_gain


def iter_elo(results: list[dict]) -> Iterator[tuple[dict, dict[str, float]]]:
    """Yield (result, ratings before it) in replay order, for every result.

    The snapshot is taken before this result's participants are seeded, so it
    only holds players with at least one previously rated game."""
    ratings: dict[str, float] = {}
    for r in _ordered(results):
        yield r, dict(ratings)
        _apply(ratings, r)


def compute_elo(results: list[dict]) -> dict[str, int]:
    """Replay results chronologically; winner duels each other participant pairwise."""
    ratings: dict[str, float] = {}
    for r in _ordered(results):
        _apply(ratings, r)
    return {pid: round(rating) for pid, rating in ratings.items()}


def leaders_before(results: list[dict]) -> dict[str, str | None]:
    """Result pk -> the sole #1 (by rounded rating, as the leaderboard shows it)
    going into that result; None when nobody is rated yet or the top is tied."""
    leaders: dict[str, str | None] = {}
    for r, snapshot in iter_elo(results):
        pk = r.get("pk")
        if not pk:
            continue
        rounded = {pid: round(v) for pid, v in snapshot.items()}
        if not rounded:
            leaders[pk] = None
            continue
        top = max(rounded.values())
        at_top = [pid for pid, v in rounded.items() if v == top]
        leaders[pk] = at_top[0] if len(at_top) == 1 else None
    return leaders
