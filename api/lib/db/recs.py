from __future__ import annotations

import lib.db.base as _db


def list_recs() -> list[dict]:
    return _db.paginated_scan(_db.tables["recs"])


def get_rec(rec_id: str) -> dict | None:
    return _db.tables["recs"].get_item(Key={"pk": rec_id}).get("Item")


def put_rec(item: dict) -> None:
    _db.tables["recs"].put_item(Item=_db._floats_to_decimal(item))


def delete_rec(rec_id: str) -> None:
    _db.tables["recs"].delete_item(Key={"pk": rec_id})
