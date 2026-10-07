from __future__ import annotations

import contextlib
from datetime import UTC, datetime

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


def set_user_fields(username: str, fields: dict, *, bump_token_version: bool = False) -> None:
    """Partial update; a missing user is a no-op. Never read-modify-write the
    whole users record: a concurrent role change or logout would be undone."""
    with contextlib.suppress(_db.ItemNotFoundError):
        _db.tables["users"].set_fields(
            username, fields, increment="tokenVersion" if bump_token_version else None
        )


def update_avatar(username: str, has_avatar: bool) -> None:
    # Stamps the change so avatar URLs can be cache-busted; without it a
    # replaced avatar keeps the same URL and browsers show the old one for
    # as long as the Cache-Control max-age allows.
    set_user_fields(
        username, {"hasAvatar": has_avatar, "avatarUpdatedAt": datetime.now(UTC).isoformat()}
    )


def set_last_read_at(username: str, timestamp: str) -> None:
    set_user_fields(username, {"lastReadAt": timestamp})


def delete_user(username: str) -> None:
    _db.tables["users"].delete_item(Key={"pk": username})
