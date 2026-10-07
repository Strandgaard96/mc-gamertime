from __future__ import annotations

from dataclasses import dataclass, field

from lib.elo import leaders_before

from .defs import ACHIEVEMENT_DEFS


@dataclass
class AchievementContext:
    player_id: str
    games_by_id: dict[str, dict]
    # result pk -> sole #1 ELO player going into that result (None: no sole leader)
    leader_before: dict[str, str | None] = field(default_factory=dict)

    def my_entry(self, result: dict) -> dict | None:
        return next((p for p in result["players"] if p.get("playerId") == self.player_id), None)

    def game(self, result: dict) -> dict:
        return self.games_by_id.get(result.get("gameId"), {})


def compute_achievements(
    player_id: str,
    results: list[dict],
    games_by_id: dict[str, dict],
    leader_before: dict[str, str | None] | None = None,
) -> list[dict]:
    """`results` must be ALL results (not just this player's): the leader map
    depends on everyone's ratings. Callers evaluating many players over the
    same list should compute `leaders_before(results)` once and pass it in."""
    player_results = sorted(
        [r for r in results if any(p.get("playerId") == player_id for p in r["players"])],
        key=lambda r: r["date"],
    )
    ctx = AchievementContext(
        player_id,
        games_by_id,
        leader_before if leader_before is not None else leaders_before(results),
    )
    return [
        {
            "id": d["id"],
            "label": d["label"],
            "description": d["description"],
            "icon": d["icon"],
            "earnedAt": d["evaluate"](ctx, player_results),
        }
        for d in ACHIEVEMENT_DEFS
    ]
