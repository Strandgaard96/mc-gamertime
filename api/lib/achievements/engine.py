from __future__ import annotations

from dataclasses import dataclass

from .defs import ACHIEVEMENT_DEFS


@dataclass
class AchievementContext:
    player_id: str
    games_by_id: dict[str, dict]

    def my_entry(self, result: dict) -> dict | None:
        return next((p for p in result["players"] if p.get("playerId") == self.player_id), None)

    def game(self, result: dict) -> dict:
        return self.games_by_id.get(result.get("gameId"), {})


def compute_achievements(
    player_id: str, results: list[dict], games_by_id: dict[str, dict]
) -> list[dict]:
    player_results = sorted(
        [r for r in results if any(p.get("playerId") == player_id for p in r["players"])],
        key=lambda r: r["date"],
    )
    ctx = AchievementContext(player_id, games_by_id)
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
