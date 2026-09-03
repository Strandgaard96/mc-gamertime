from __future__ import annotations

import lib.db.base as _db


def list_posts() -> list[dict]:
    return _db.paginated_scan(_db.tables["posts"])


def get_post(post_id: str) -> dict | None:
    return _db.tables["posts"].get_item(Key={"pk": post_id}).get("Item")


def put_post(item: dict) -> None:
    _db.tables["posts"].put_item(Item=_db._floats_to_decimal(item))


def delete_post(post_id: str) -> None:
    _db.tables["posts"].delete_item(Key={"pk": post_id})
