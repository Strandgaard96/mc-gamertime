import pytest

from lib.db.base import ItemNotFoundError
from lib.db.sqlite_backend import SqliteTable, make_sqlite_tables


@pytest.fixture
def table(tmp_path):
    return SqliteTable(str(tmp_path / "test.db"), "games")


def test_put_and_get_item_round_trips(table):
    table.put_item(Item={"pk": "01GAME", "name": "Wingspan", "minPlayers": 1})
    result = table.get_item(Key={"pk": "01GAME"})
    assert result == {"Item": {"pk": "01GAME", "name": "Wingspan", "minPlayers": 1}}


def test_get_item_missing_returns_empty_dict(table):
    assert table.get_item(Key={"pk": "nope"}) == {}


def test_put_item_overwrites_existing(table):
    table.put_item(Item={"pk": "01GAME", "name": "Wingspan"})
    table.put_item(Item={"pk": "01GAME", "name": "Wingspan v2"})
    assert table.get_item(Key={"pk": "01GAME"})["Item"]["name"] == "Wingspan v2"


def test_delete_item_removes_row(table):
    table.put_item(Item={"pk": "01GAME", "name": "Wingspan"})
    table.delete_item(Key={"pk": "01GAME"})
    assert table.get_item(Key={"pk": "01GAME"}) == {}


def test_scan_returns_all_items(table):
    table.put_item(Item={"pk": "a", "name": "A"})
    table.put_item(Item={"pk": "b", "name": "B"})
    result = table.scan()
    assert sorted(i["pk"] for i in result["Items"]) == ["a", "b"]


def test_put_item_converts_decimal_to_jsonable(table):
    from decimal import Decimal

    table.put_item(Item={"pk": "01RESULT", "score": Decimal("4.5"), "count": Decimal("3")})
    item = table.get_item(Key={"pk": "01RESULT"})["Item"]
    assert item["score"] == 4.5
    assert item["count"] == 3


def test_add_to_set_creates_field_when_absent(table):
    table.put_item(Item={"pk": "01GAME", "name": "Wingspan"})
    table.add_to_set("01GAME", "favorites", "alice")
    item = table.get_item(Key={"pk": "01GAME"})["Item"]
    assert item["favorites"] == ["alice"]


def test_add_to_set_is_idempotent(table):
    table.put_item(Item={"pk": "01GAME", "name": "Wingspan", "favorites": ["alice"]})
    table.add_to_set("01GAME", "favorites", "alice")
    item = table.get_item(Key={"pk": "01GAME"})["Item"]
    assert item["favorites"] == ["alice"]


def test_add_to_set_missing_pk_raises_item_not_found(table):
    with pytest.raises(ItemNotFoundError):
        table.add_to_set("nope", "favorites", "alice")


def test_remove_from_set_removes_value(table):
    table.put_item(Item={"pk": "01GAME", "name": "Wingspan", "favorites": ["alice", "bob"]})
    table.remove_from_set("01GAME", "favorites", "alice")
    item = table.get_item(Key={"pk": "01GAME"})["Item"]
    assert item["favorites"] == ["bob"]


def test_remove_from_set_missing_pk_raises_item_not_found(table):
    with pytest.raises(ItemNotFoundError):
        table.remove_from_set("nope", "favorites", "alice")


def test_increment_with_timestamp_creates_item_when_absent(tmp_path):
    table = SqliteTable(str(tmp_path / "test.db"), "users")
    table.increment_with_timestamp(
        "admin", "failedAttempts", "lastFailureAt", "2026-01-01T00:00:00Z"
    )
    item = table.get_item(Key={"pk": "admin"})["Item"]
    assert item == {
        "pk": "admin",
        "failedAttempts": 1,
        "lastFailureAt": "2026-01-01T00:00:00Z",
    }


def test_increment_with_timestamp_increments_existing_counter(tmp_path):
    table = SqliteTable(str(tmp_path / "test.db"), "users")
    table.put_item(Item={"pk": "admin", "failedAttempts": 2})
    table.increment_with_timestamp(
        "admin", "failedAttempts", "lastFailureAt", "2026-01-01T00:00:00Z"
    )
    item = table.get_item(Key={"pk": "admin"})["Item"]
    assert item["failedAttempts"] == 3
    assert item["lastFailureAt"] == "2026-01-01T00:00:00Z"


def test_data_persists_across_separate_connections(tmp_path):
    db_path = str(tmp_path / "test.db")
    SqliteTable(db_path, "games").put_item(Item={"pk": "01GAME", "name": "Wingspan"})
    reopened = SqliteTable(db_path, "games")
    assert reopened.get_item(Key={"pk": "01GAME"})["Item"]["name"] == "Wingspan"


def test_make_sqlite_tables_returns_all_seven_logical_tables(tmp_path):
    tables = make_sqlite_tables(str(tmp_path / "test.db"))
    assert set(tables) == {
        "users",
        "games",
        "results",
        "posts",
        "recs",
        "reactions",
        "notifications",
        "settings",
    }
    assert isinstance(tables["games"], SqliteTable)
