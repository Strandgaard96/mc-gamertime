from __future__ import annotations

from datetime import datetime, timezone

import lib.db.base as _db


def get_user(username: str) -> dict | None:
    return _db.tables["users"].get_item(Key={"pk": username}).get("Item")


def list_users() -> list[dict]:
    return _db.paginated_scan(_db.tables["users"])


def put_user(item: dict) -> None:
    _db.tables["users"].put_item(Item=_db._floats_to_decimal(item))


def record_failed_login(username: str, timestamp: str) -> None:
    # Atomic ADD avoids the read-modify-write race when parallel logins fail
    _db.tables["users"].increment_with_timestamp(
        username, "failedAttempts", "lastFailureAt", timestamp
    )


def update_avatar(username: str, has_avatar: bool) -> None:
    item = _db.tables["users"].get_item(Key={"pk": username}).get("Item")
    if item:
        item["hasAvatar"] = has_avatar
        # Stamps the change so avatar URLs can be cache-busted; without it a
        # replaced avatar keeps the same URL and browsers show the old one for
        # as long as the Cache-Control max-age allows.
        item["avatarUpdatedAt"] = datetime.now(timezone.utc).isoformat()
        _db.tables["users"].put_item(Item=_db._floats_to_decimal(item))


def set_last_read_at(username: str, timestamp: str) -> None:
    item = _db.tables["users"].get_item(Key={"pk": username}).get("Item")
    if item:
        item["lastReadAt"] = timestamp
        _db.tables["users"].put_item(Item=_db._floats_to_decimal(item))


def delete_user(username: str) -> None:
    _db.tables["users"].delete_item(Key={"pk": username})
