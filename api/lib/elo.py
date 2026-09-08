from __future__ import annotations

START_RATING = 1000.0
K = 32.0


def compute_elo(results: list[dict]) -> dict[str, int]:
    """Replay results chronologically; winner duels each other participant pairwise."""
    ordered = sorted(results, key=lambda r: (r["date"], r.get("createdAt", "")))
    ratings: dict[str, float] = {}

    for r in ordered:
        player_ids = [p["playerId"] for p in r.get("players", []) if p.get("playerId")]
        winner_id = r.get("winnerId")
        if len(player_ids) < 2 or winner_id not in player_ids:
            continue

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

    return {pid: round(rating) for pid, rating in ratings.items()}
