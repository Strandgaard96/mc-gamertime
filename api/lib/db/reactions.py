from __future__ import annotations

import lib.db.base as _db


def list_reactions() -> list[dict]:
    return _db.paginated_scan(_db.tables["reactions"])


def find_reaction(session_pk: str, emoji: str, user_id: str) -> dict | None:
    """The one reaction a given user put on a given session, if any."""
    matches = _db.paginated_scan(
        _db.tables["reactions"],
        filters={
            "type": "reaction",
            "sessionPk": session_pk,
            "emoji": emoji,
            "userId": user_id,
        },
    )
    return matches[0] if matches else None


def get_reaction(pk: str) -> dict | None:
    return _db.tables["reactions"].get_item(Key={"pk": pk}).get("Item")


def put_reaction(item: dict) -> None:
    _db.tables["reactions"].put_item(Item=_db._floats_to_decimal(item))


def delete_reaction(pk: str) -> None:
    _db.tables["reactions"].delete_item(Key={"pk": pk})
