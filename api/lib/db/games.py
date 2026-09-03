from __future__ import annotations

import lib.db.base as _db
from lib.db.base import ItemNotFoundError


def list_games() -> list[dict]:
    return _db.paginated_scan(_db.tables["games"])


def get_game(game_id: str) -> dict | None:
    return _db.tables["games"].get_item(Key={"pk": game_id}).get("Item")


def put_game(item: dict) -> None:
    _db.tables["games"].put_item(Item=_db._floats_to_decimal(item))


def delete_game(game_id: str) -> None:
    _db.tables["games"].delete_item(Key={"pk": game_id})


class GameNotFoundError(Exception):
    pass


def add_favourite(game_id: str, user_id: str) -> None:
    try:
        _db.tables["games"].add_to_set(game_id, "favorites", user_id)
    except ItemNotFoundError:
        raise GameNotFoundError(game_id)


def remove_favourite(game_id: str, user_id: str) -> None:
    try:
        _db.tables["games"].remove_from_set(game_id, "favorites", user_id)
    except ItemNotFoundError:
        raise GameNotFoundError(game_id)
