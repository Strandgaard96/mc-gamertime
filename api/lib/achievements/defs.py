from __future__ import annotations

from .rules import (
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


def _dominant(ctx, player_results):
    wins = played = 0
    for r in player_results:
        played += 1
        if is_win(ctx, r):
            wins += 1
        if played >= 10 and wins / played >= 0.7:
            return r["date"]
    return None


ACHIEVEMENT_DEFS: list[dict] = [
    {
        "id": "first_win",
        "label": "First Blood",
        "icon": "🏆",
        "description": "Won your first game",
        "evaluate": counter_threshold(is_win, 1),
    },
    {
        "id": "streak_3",
        "label": "Hat Trick",
        "icon": "🎩",
        "description": "Won 3 games in a row",
        "evaluate": streak_threshold(is_win, 3),
    },
    {
        "id": "streak_5",
        "label": "On Fire",
        "icon": "🔥",
        "description": "Won 5 games in a row",
        "evaluate": streak_threshold(is_win, 5),
    },
    {
        "id": "games_10",
        "label": "Regular",
        "icon": "🎲",
        "description": "Played 10 games",
        "evaluate": counter_threshold(lambda ctx, r: True, 10),
    },
    {
        "id": "games_25",
        "label": "Veteran",
        "icon": "⭐",
        "description": "Played 25 games",
        "evaluate": counter_threshold(lambda ctx, r: True, 25),
    },
    {
        "id": "wins_10",
        "label": "Champion",
        "icon": "🥇",
        "description": "Won 10 games",
        "evaluate": counter_threshold(is_win, 10),
    },
    {
        "id": "wins_25",
        "label": "Legend",
        "icon": "👑",
        "description": "Won 25 games",
        "evaluate": counter_threshold(is_win, 25),
    },
    {
        "id": "dominant",
        "label": "Dominant",
        "icon": "💪",
        "description": "Win rate ≥ 70% with at least 10 games played",
        "evaluate": _dominant,
    },
    {
        "id": "perfect_10",
        "label": "Perfect 10",
        "icon": "🎯",
        "description": "Scored a perfect 10",
        "evaluate": counter_threshold(score_at_least(10), 1),
    },
    # --- game-attribute-based ---
    {
        "id": "explorer_10",
        "label": "Explorer",
        "icon": "🧭",
        "description": "Played 10 different games",
        "evaluate": distinct_count_threshold(lambda ctx, r: r["gameId"], 10),
    },
    {
        "id": "heavyweight",
        "label": "Heavyweight Champion",
        "icon": "🏋️",
        "description": "Won a game with weight ≥ 4.0",
        "evaluate": counter_threshold(all_of(is_win, game_weight_at_least(4.0)), 1),
    },
    {
        "id": "party_winner",
        "label": "Party Animal",
        "icon": "🎉",
        "description": "Won a game tagged 'party'",
        "evaluate": counter_threshold(all_of(is_win, game_has_tag("party")), 1),
    },
    {
        "id": "harkonnen_5",
        "label": "House Harkonnen",
        "icon": "⚔️",
        "description": "Won 5 games as Harkonnen in Dune: Imperium",
        "evaluate": counter_threshold(
            all_of(is_win, game_name_is("Dune: Imperium"), variable_equals("Faction", "Harkonnen")),
            5,
        ),
    },
]
