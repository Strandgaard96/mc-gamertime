from __future__ import annotations

from .rules import (
    all_of,
    beat_the_leader,
    comeback_after,
    counter_threshold,
    distinct_count_threshold,
    game_has_tag,
    game_name_is,
    game_play_time_at_least,
    game_weight_at_least,
    is_win,
    per_key_counter_threshold,
    player_count_at_least,
    score_at_least,
    streak_threshold,
    variable_equals,
)


def _dominant(ctx, player_results):
    wins = 0
    for played, r in enumerate(player_results, start=1):
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
        "id": "games_50",
        "label": "Half Century",
        "icon": "🏅",
        "description": "Played 50 games",
        "evaluate": counter_threshold(lambda ctx, r: True, 50),
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
    {
        "id": "giant_slayer",
        "label": "Giant Slayer",
        "icon": "🗡️",
        "description": "Beat the #1 ranked player",
        "evaluate": counter_threshold(beat_the_leader, 1),
    },
    {
        "id": "comeback",
        "label": "Comeback Kid",
        "icon": "🔄",
        "description": "Won a game after losing 5 or more in a row",
        "evaluate": comeback_after(5),
    },
    {
        "id": "polymath",
        "label": "Polymath",
        "icon": "🎓",
        "description": "Won 10 different games",
        "evaluate": distinct_count_threshold(lambda ctx, r: r["gameId"], 10, predicate=is_win),
    },
    {
        "id": "specialist",
        "label": "Specialist",
        "icon": "🔁",
        "description": "Won the same game 5 times",
        "evaluate": per_key_counter_threshold(is_win, lambda ctx, r: r["gameId"], 5),
    },
    {
        "id": "marathon",
        "label": "Marathon",
        "icon": "⏳",
        "description": "Won a game with a play time of 2 hours or more",
        "evaluate": counter_threshold(all_of(is_win, game_play_time_at_least(120)), 1),
    },
    {
        "id": "crowd_pleaser",
        "label": "Crowd Pleaser",
        "icon": "👥",
        "description": "Won a game with 5 or more players",
        "evaluate": counter_threshold(all_of(is_win, player_count_at_least(5)), 1),
    },
]
