from __future__ import annotations

from collections.abc import Callable
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from .engine import AchievementContext

Predicate = Callable[["AchievementContext", dict], bool]
Evaluate = Callable[["AchievementContext", list[dict]], "str | None"]


def is_win(ctx: AchievementContext, result: dict) -> bool:
    return result.get("winnerId") == ctx.player_id


def score_at_least(n: float) -> Predicate:
    def pred(ctx: AchievementContext, result: dict) -> bool:
        entry = ctx.my_entry(result)
        return entry is not None and entry.get("score") is not None and float(entry["score"]) >= n

    return pred


def game_weight_at_least(weight: float) -> Predicate:
    def pred(ctx: AchievementContext, result: dict) -> bool:
        game_weight = ctx.game(result).get("weight")
        return game_weight is not None and float(game_weight) >= weight

    return pred


def game_has_tag(tag: str) -> Predicate:
    def pred(ctx: AchievementContext, result: dict) -> bool:
        tags = ctx.game(result).get("tags") or []
        return tag.lower() in (t.lower() for t in tags)

    return pred


def game_name_is(name: str) -> Predicate:
    def pred(ctx: AchievementContext, result: dict) -> bool:
        return result.get("gameName", "").lower() == name.lower()

    return pred


def variable_equals(label: str, value: str) -> Predicate:
    def pred(ctx: AchievementContext, result: dict) -> bool:
        entry = ctx.my_entry(result)
        if entry is None:
            return False
        var_def = next(
            (
                v
                for v in ctx.game(result).get("playerVariables", [])
                if v["label"].lower() == label.lower()
            ),
            None,
        )
        if var_def is None:
            return False
        return (entry.get("variables") or {}).get(var_def["id"]) == value

    return pred


def all_of(*predicates: Predicate) -> Predicate:
    def pred(ctx: AchievementContext, result: dict) -> bool:
        return all(p(ctx, result) for p in predicates)

    return pred


def counter_threshold(predicate: Predicate, threshold: int) -> Evaluate:
    """Earned when the running count of matching results reaches threshold."""

    def evaluate(ctx: AchievementContext, player_results: list[dict]) -> str | None:
        count = 0
        for r in player_results:
            if predicate(ctx, r):
                count += 1
                if count == threshold:
                    return r["date"]
        return None

    return evaluate


def streak_threshold(predicate: Predicate, length: int) -> Evaluate:
    """Earned when a consecutive run of matching results first reaches length."""

    def evaluate(ctx: AchievementContext, player_results: list[dict]) -> str | None:
        streak = 0
        for r in player_results:
            if predicate(ctx, r):
                streak += 1
                if streak >= length:
                    return r["date"]
            else:
                streak = 0
        return None

    return evaluate


def distinct_count_threshold(
    key_fn: Callable[[AchievementContext, dict], object], threshold: int
) -> Evaluate:
    """Earned when the running set of distinct key_fn(ctx, result) values reaches threshold."""

    def evaluate(ctx: AchievementContext, player_results: list[dict]) -> str | None:
        seen = set()
        for r in player_results:
            seen.add(key_fn(ctx, r))
            if len(seen) == threshold:
                return r["date"]
        return None

    return evaluate
