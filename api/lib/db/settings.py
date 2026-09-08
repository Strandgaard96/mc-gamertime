from __future__ import annotations

import lib.db.base as _db

_PK = "instance"


def get_settings() -> dict:
    return _db.tables["settings"].get_item(Key={"pk": _PK}).get("Item", {})


def put_settings(item: dict) -> None:
    _db.tables["settings"].put_item(Item=_db._floats_to_decimal(item))
