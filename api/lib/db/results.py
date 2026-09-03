from __future__ import annotations

import lib.db.base as _db


def list_results() -> list[dict]:
    return _db.paginated_scan(_db.tables["results"])


def get_result(pk: str) -> dict | None:
    resp = _db.tables["results"].get_item(Key={"pk": pk})
    return resp.get("Item")


def put_result(item: dict) -> None:
    _db.tables["results"].put_item(Item=_db._floats_to_decimal(item))


def delete_result(pk: str) -> None:
    _db.tables["results"].delete_item(Key={"pk": pk})
