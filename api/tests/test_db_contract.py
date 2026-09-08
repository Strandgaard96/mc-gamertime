"""One suite, run against both real table backends.

`DynamoTable` and `SqliteTable` are interchangeable by convention: every caller
in lib/db/*.py takes whichever one `_make_tables()` built and calls the same
methods on it. Nothing enforced that. These tests are the enforcement — each one
runs twice, once per backend, so a behavioural difference fails here rather than
in production on whichever deployment nobody tested.

The DynamoDB side runs against moto (a dev-only dependency, deliberately absent
from requirements.txt so the Lambda bundle never sees it).
"""

from __future__ import annotations

import inspect
from decimal import Decimal

import boto3
import pytest
from moto import mock_aws

from lib.db.base import DynamoTable, ItemNotFoundError, paginated_scan
from lib.db.protocol import Table
from lib.db.sqlite_backend import SqliteTable


@pytest.fixture
def sqlite_table(tmp_path):
    return SqliteTable(str(tmp_path / "contract.db"), "games")


@pytest.fixture
def dynamo_table():
    with mock_aws():
        ddb = boto3.resource("dynamodb", region_name="eu-west-1")
        ddb.create_table(
            TableName="games",
            KeySchema=[{"AttributeName": "pk", "KeyType": "HASH"}],
            AttributeDefinitions=[{"AttributeName": "pk", "AttributeType": "S"}],
            BillingMode="PAY_PER_REQUEST",
        )
        yield DynamoTable(ddb.Table("games"))


@pytest.fixture(params=["sqlite", "dynamo"])
def table(request):
    """Every test below runs once per backend."""
    return request.getfixturevalue(f"{request.param}_table")


# --- shape ---------------------------------------------------------------


@pytest.mark.parametrize("impl", [DynamoTable, SqliteTable])
def test_backend_satisfies_the_table_protocol(impl):
    assert issubclass(impl, Table)


def test_backends_agree_on_method_signatures():
    """A renamed keyword or a dropped parameter on one backend is a silent
    production break on the other deployment. Compare them here instead."""
    methods = [n for n in vars(Table) if not n.startswith("_")]
    assert methods, "the protocol declares no methods to compare"
    for name in methods:
        dynamo_sig = inspect.signature(getattr(DynamoTable, name))
        sqlite_sig = inspect.signature(getattr(SqliteTable, name))
        assert [(p.name, p.kind) for p in dynamo_sig.parameters.values()] == [
            (p.name, p.kind) for p in sqlite_sig.parameters.values()
        ], f"{name}() differs between backends"


# --- round trip ----------------------------------------------------------


def test_put_then_get_returns_the_item(table):
    table.put_item(Item={"pk": "g1", "name": "Catan", "tags": ["classic"]})
    assert table.get_item(Key={"pk": "g1"})["Item"]["name"] == "Catan"


def test_get_missing_item_returns_no_item_key(table):
    assert "Item" not in table.get_item(Key={"pk": "nope"})


def test_put_overwrites_an_existing_pk(table):
    table.put_item(Item={"pk": "g1", "name": "Catan"})
    table.put_item(Item={"pk": "g1", "name": "Wingspan"})
    assert table.get_item(Key={"pk": "g1"})["Item"]["name"] == "Wingspan"


def test_delete_removes_the_item(table):
    table.put_item(Item={"pk": "g1", "name": "Catan"})
    table.delete_item(Key={"pk": "g1"})
    assert "Item" not in table.get_item(Key={"pk": "g1"})


def test_delete_of_a_missing_item_is_not_an_error(table):
    table.delete_item(Key={"pk": "ghost"})


def test_scan_returns_every_item(table):
    table.put_item(Item={"pk": "g1", "name": "Catan"})
    table.put_item(Item={"pk": "g2", "name": "Wingspan"})
    assert {i["name"] for i in table.scan()["Items"]} == {"Catan", "Wingspan"}


def test_decimals_round_trip_as_numbers(table):
    table.put_item(Item={"pk": "g1", "weight": Decimal("2.5"), "plays": Decimal(3)})
    item = table.get_item(Key={"pk": "g1"})["Item"]
    assert float(item["weight"]) == 2.5
    assert int(item["plays"]) == 3


def test_nested_structures_round_trip(table):
    table.put_item(
        Item={"pk": "r1", "players": [{"playerId": "alice", "score": Decimal(10)}], "meta": {}}
    )
    item = table.get_item(Key={"pk": "r1"})["Item"]
    assert item["players"][0]["playerId"] == "alice"
    assert int(item["players"][0]["score"]) == 10


# --- set operations ------------------------------------------------------


def test_add_to_set_creates_and_extends(table):
    table.put_item(Item={"pk": "g1", "name": "Catan"})
    table.add_to_set("g1", "favorites", "alice")
    table.add_to_set("g1", "favorites", "bob")
    assert set(table.get_item(Key={"pk": "g1"})["Item"]["favorites"]) == {"alice", "bob"}


def test_add_to_set_is_idempotent(table):
    table.put_item(Item={"pk": "g1", "name": "Catan"})
    table.add_to_set("g1", "favorites", "alice")
    table.add_to_set("g1", "favorites", "alice")
    assert set(table.get_item(Key={"pk": "g1"})["Item"]["favorites"]) == {"alice"}


def test_remove_from_set_drops_the_member(table):
    table.put_item(Item={"pk": "g1", "name": "Catan"})
    table.add_to_set("g1", "favorites", "alice")
    table.add_to_set("g1", "favorites", "bob")
    table.remove_from_set("g1", "favorites", "alice")
    assert set(table.get_item(Key={"pk": "g1"})["Item"]["favorites"]) == {"bob"}


def test_set_operations_on_a_missing_pk_raise(table):
    with pytest.raises(ItemNotFoundError):
        table.add_to_set("ghost", "favorites", "alice")
    with pytest.raises(ItemNotFoundError):
        table.remove_from_set("ghost", "favorites", "alice")


# --- counters ------------------------------------------------------------


def test_increment_creates_the_item_when_absent(table):
    table.increment_with_timestamp("g1", "playCount", "lastPlayed", "2026-01-01T00:00:00Z")
    item = table.get_item(Key={"pk": "g1"})["Item"]
    assert int(item["playCount"]) == 1
    assert item["lastPlayed"] == "2026-01-01T00:00:00Z"


def test_increment_accumulates(table):
    table.increment_with_timestamp("g1", "playCount", "lastPlayed", "2026-01-01T00:00:00Z")
    table.increment_with_timestamp("g1", "playCount", "lastPlayed", "2026-02-02T00:00:00Z")
    item = table.get_item(Key={"pk": "g1"})["Item"]
    assert int(item["playCount"]) == 2
    assert item["lastPlayed"] == "2026-02-02T00:00:00Z"


# --- filtered scan -------------------------------------------------------


def test_paginated_scan_without_filters_returns_everything(table):
    table.put_item(Item={"pk": "n1", "playerId": "alice"})
    table.put_item(Item={"pk": "n2", "playerId": "bob"})
    assert len(paginated_scan(table)) == 2


def test_paginated_scan_filters_on_a_string_attribute(table):
    table.put_item(Item={"pk": "n1", "playerId": "alice"})
    table.put_item(Item={"pk": "n2", "playerId": "bob"})
    table.put_item(Item={"pk": "n3", "playerId": "alice"})
    items = paginated_scan(table, filters={"playerId": "alice"})
    assert {i["pk"] for i in items} == {"n1", "n3"}


def test_paginated_scan_filters_on_several_attributes(table):
    table.put_item(Item={"pk": "n1", "playerId": "alice", "kind": "achievement"})
    table.put_item(Item={"pk": "n2", "playerId": "alice", "kind": "milestone"})
    items = paginated_scan(table, filters={"playerId": "alice", "kind": "milestone"})
    assert {i["pk"] for i in items} == {"n2"}


def test_paginated_scan_filters_on_numbers(table):
    table.put_item(Item={"pk": "g1", "weight": Decimal("2.5")})
    table.put_item(Item={"pk": "g2", "weight": Decimal("3.5")})
    items = paginated_scan(table, filters={"weight": Decimal("2.5")})
    assert {i["pk"] for i in items} == {"g1"}


def test_paginated_scan_filter_matching_nothing_returns_empty(table):
    table.put_item(Item={"pk": "n1", "playerId": "alice"})
    assert paginated_scan(table, filters={"playerId": "nobody"}) == []


def test_items_absent_the_filtered_attribute_are_excluded(table):
    table.put_item(Item={"pk": "n1", "playerId": "alice"})
    table.put_item(Item={"pk": "n2"})
    assert {i["pk"] for i in paginated_scan(table, filters={"playerId": "alice"})} == {"n1"}
