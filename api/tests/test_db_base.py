from unittest.mock import MagicMock

import boto3

from lib.db.base import paginated_scan


def test_paginated_scan_follows_last_evaluated_key():
    table = MagicMock()
    table.scan.side_effect = [
        {"Items": [{"pk": "a"}], "LastEvaluatedKey": {"pk": "a"}},
        {"Items": [{"pk": "b"}]},
    ]
    result = paginated_scan(table)
    assert result == [{"pk": "a"}, {"pk": "b"}]
    assert table.scan.call_count == 2
    table.scan.assert_called_with(ExclusiveStartKey={"pk": "a"})


def test_paginated_scan_single_page():
    table = MagicMock()
    table.scan.return_value = {"Items": [{"pk": "a"}, {"pk": "b"}]}
    result = paginated_scan(table)
    assert result == [{"pk": "a"}, {"pk": "b"}]
    assert table.scan.call_count == 1


import lib.db.base as db_base  # noqa: E402


class _FakeDynamoResource:
    def Table(self, name):
        return name


def test_make_tables_uses_dynamodb_endpoint_url(monkeypatch):
    monkeypatch.setenv("DYNAMODB_ENDPOINT_URL", "http://dynamodb-local:8000")
    captured = {}

    def fake_resource(service, **kwargs):
        captured.update(kwargs)
        return _FakeDynamoResource()

    monkeypatch.setattr(boto3, "resource", fake_resource)

    db_base._make_tables()

    assert captured["endpoint_url"] == "http://dynamodb-local:8000"
    assert captured["aws_access_key_id"] == "local"
    assert captured["aws_secret_access_key"] == "local"


def test_make_tables_without_endpoint_url_omits_local_creds(monkeypatch):
    monkeypatch.delenv("DYNAMODB_ENDPOINT_URL", raising=False)
    captured = {}

    def fake_resource(service, **kwargs):
        captured.update(kwargs)
        return _FakeDynamoResource()

    monkeypatch.setattr(boto3, "resource", fake_resource)

    db_base._make_tables()

    assert "endpoint_url" not in captured
    assert "aws_access_key_id" not in captured


from lib.db.base import DynamoTable, ItemNotFoundError  # noqa: E402


def test_dynamo_table_add_to_set_calls_update_item():
    inner = MagicMock()
    table = DynamoTable(inner)
    table.add_to_set("01GAME", "favorites", "alice")
    _, kwargs = inner.update_item.call_args
    assert kwargs["Key"] == {"pk": "01GAME"}
    assert kwargs["UpdateExpression"] == "ADD favorites :v"
    assert kwargs["ExpressionAttributeValues"] == {":v": {"alice"}}


def test_dynamo_table_add_to_set_raises_item_not_found_on_conditional_check_failure():
    from botocore.exceptions import ClientError

    inner = MagicMock()
    inner.update_item.side_effect = ClientError(
        {"Error": {"Code": "ConditionalCheckFailedException", "Message": "x"}}, "UpdateItem"
    )
    table = DynamoTable(inner)
    try:
        table.add_to_set("missing", "favorites", "alice")
        assert False, "expected ItemNotFoundError"
    except ItemNotFoundError as e:
        assert str(e) == "missing"


def test_dynamo_table_remove_from_set_calls_update_item():
    inner = MagicMock()
    table = DynamoTable(inner)
    table.remove_from_set("01GAME", "favorites", "alice")
    _, kwargs = inner.update_item.call_args
    assert kwargs["UpdateExpression"] == "DELETE favorites :v"
    assert kwargs["ExpressionAttributeValues"] == {":v": {"alice"}}


def test_dynamo_table_increment_with_timestamp_calls_update_item():
    inner = MagicMock()
    table = DynamoTable(inner)
    table.increment_with_timestamp(
        "admin", "failedAttempts", "lastFailureAt", "2026-01-01T00:00:00Z"
    )
    _, kwargs = inner.update_item.call_args
    assert kwargs["Key"] == {"pk": "admin"}
    assert kwargs["UpdateExpression"] == "ADD failedAttempts :one SET lastFailureAt = :ts"
    assert kwargs["ExpressionAttributeValues"] == {
        ":one": 1,
        ":ts": "2026-01-01T00:00:00Z",
    }


def test_dynamo_table_passthrough_methods_delegate_to_inner():
    inner = MagicMock()
    table = DynamoTable(inner)
    table.get_item(Key={"pk": "x"})
    table.put_item(Item={"pk": "x"})
    table.delete_item(Key={"pk": "x"})
    table.scan()
    inner.get_item.assert_called_once_with(Key={"pk": "x"})
    inner.put_item.assert_called_once_with(Item={"pk": "x"})
    inner.delete_item.assert_called_once_with(Key={"pk": "x"})
    inner.scan.assert_called_once_with()


def test_make_tables_uses_sqlite_backend_when_db_backend_sqlite(monkeypatch, tmp_path):
    from lib.db.sqlite_backend import SqliteTable

    monkeypatch.setenv("DB_BACKEND", "sqlite")
    monkeypatch.setenv("SQLITE_DB_PATH", str(tmp_path / "test.db"))

    tables = db_base._make_tables()

    assert isinstance(tables["games"], SqliteTable)
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
