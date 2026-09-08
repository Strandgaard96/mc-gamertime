from __future__ import annotations

import lib.db.base as _db


def list_notifications_for_player(player_id: str) -> list[dict]:
    items = _db.paginated_scan(_db.tables["notifications"], filters={"playerId": player_id})
    return sorted(items, key=lambda n: n["createdAt"], reverse=True)


def put_notification(item: dict) -> None:
    _db.tables["notifications"].put_item(Item=_db._floats_to_decimal(item))
