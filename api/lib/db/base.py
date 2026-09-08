from __future__ import annotations

import os
import sqlite3
from decimal import Decimal

# boto3/botocore are imported lazily below: the selfhost image ships without the
# AWS SDK (api/requirements-selfhost.txt), and this module is imported on every
# deployment.


class ItemNotFoundError(Exception):
    """Raised by add_to_set/remove_from_set/increment_with_timestamp when pk
    doesn't exist and the operation requires it to (mirrors DynamoDB's
    ConditionExpression=Attr("pk").exists())."""


class DynamoTable:
    """Wraps a boto3 DynamoDB Table resource, adding semantic update methods
    so callers in lib/db/*.py never write raw UpdateExpression strings."""

    def __init__(self, table):
        self._table = table

    def get_item(self, *, Key: dict) -> dict:
        return self._table.get_item(Key=Key)

    def put_item(self, *, Item: dict) -> None:
        self._table.put_item(Item=Item)

    def delete_item(self, *, Key: dict) -> None:
        self._table.delete_item(Key=Key)

    def scan(self, **kwargs) -> dict:
        filters = kwargs.pop("Filters", None)
        if filters:
            # Equality only, which is all any caller needs. Note this is a
            # server-side filter, not an index: DynamoDB still reads the whole
            # table and charges for it, so this cuts payload, not RCU. A GSI is
            # the fix for that, and it lives in Terraform.
            from boto3.dynamodb.conditions import Attr

            expr = None
            for key, value in filters.items():
                cond = Attr(key).eq(_floats_to_decimal(value))
                expr = cond if expr is None else expr & cond
            kwargs["FilterExpression"] = expr
        return self._table.scan(**kwargs)

    def add_to_set(self, pk: str, field: str, value) -> None:
        from boto3.dynamodb.conditions import Attr
        from botocore.exceptions import ClientError

        try:
            self._table.update_item(
                Key={"pk": pk},
                UpdateExpression=f"ADD {field} :v",
                ExpressionAttributeValues={":v": {value}},
                ConditionExpression=Attr("pk").exists(),
            )
        except ClientError as e:
            if e.response["Error"]["Code"] == "ConditionalCheckFailedException":
                raise ItemNotFoundError(pk) from e
            raise

    def remove_from_set(self, pk: str, field: str, value) -> None:
        from boto3.dynamodb.conditions import Attr
        from botocore.exceptions import ClientError

        try:
            self._table.update_item(
                Key={"pk": pk},
                UpdateExpression=f"DELETE {field} :v",
                ExpressionAttributeValues={":v": {value}},
                ConditionExpression=Attr("pk").exists(),
            )
        except ClientError as e:
            if e.response["Error"]["Code"] == "ConditionalCheckFailedException":
                raise ItemNotFoundError(pk) from e
            raise

    def increment_with_timestamp(
        self, pk: str, counter_field: str, timestamp_field: str, timestamp_value
    ) -> None:
        self._table.update_item(
            Key={"pk": pk},
            UpdateExpression=f"ADD {counter_field} :one SET {timestamp_field} = :ts",
            ExpressionAttributeValues={":one": 1, ":ts": timestamp_value},
        )


def _floats_to_decimal(obj):
    if isinstance(obj, float):
        return Decimal(str(obj))
    if isinstance(obj, dict):
        return {k: _floats_to_decimal(v) for k, v in obj.items()}
    if isinstance(obj, list):
        return [_floats_to_decimal(i) for i in obj]
    return obj


def paginated_scan(table, filters: dict | None = None) -> list[dict]:
    """Scan a whole table, optionally narrowing it to items whose attributes
    equal the given values. Pushing the filter down to the backend beats
    filtering the returned list in Python: SQLite turns it into a real WHERE
    clause, and DynamoDB stops shipping rows the caller is about to discard."""
    items: list[dict] = []
    kwargs: dict = {"Filters": filters} if filters else {}
    while True:
        resp = table.scan(**kwargs)
        items.extend(resp.get("Items", []))
        last = resp.get("LastEvaluatedKey")
        if not last:
            break
        kwargs["ExclusiveStartKey"] = last
    return items


def _make_tables() -> dict:
    # Selfhost is the default deployment: no config at all means an embedded
    # SQLite file. The cloud path sets DB_BACKEND=dynamodb explicitly in
    # infra/lambda.tf.
    if os.environ.get("DB_BACKEND", "sqlite") == "sqlite":
        from lib.db.sqlite_backend import make_sqlite_tables

        db_path = os.environ.get("SQLITE_DB_PATH", "/data/boardsite.db")
        try:
            return make_sqlite_tables(db_path)
        except sqlite3.OperationalError as exc:
            # The default path is the container's /data volume. Outside the
            # container that directory usually doesn't exist, and sqlite3's own
            # message ("unable to open database file") doesn't say which knob
            # to turn.
            raise RuntimeError(
                f"Could not open the SQLite database at {db_path}: {exc}. "
                "Set SQLITE_DB_PATH to a writable location, or DB_BACKEND=dynamodb "
                "to use AWS."
            ) from exc

    import boto3

    region = os.environ.get("AWS_REGION", "eu-west-1")
    endpoint_url = os.environ.get("DYNAMODB_ENDPOINT_URL")
    kwargs: dict = {"region_name": region}
    if endpoint_url:
        # DynamoDB Local ignores credentials but requires *something* to be
        # set — supplying them here means selfhost's .env doesn't need fake
        # AWS creds.
        kwargs.update(
            endpoint_url=endpoint_url,
            aws_access_key_id="local",
            aws_secret_access_key="local",  # noqa: S106
        )
    dynamo = boto3.resource("dynamodb", **kwargs)
    return {
        "users": DynamoTable(dynamo.Table(os.environ.get("USERS_TABLE", "boardsite-users"))),
        "games": DynamoTable(dynamo.Table(os.environ.get("GAMES_TABLE", "boardsite-games"))),
        "results": DynamoTable(dynamo.Table(os.environ.get("RESULTS_TABLE", "boardsite-results"))),
        "posts": DynamoTable(dynamo.Table(os.environ.get("POSTS_TABLE", "boardsite-posts"))),
        "recs": DynamoTable(dynamo.Table(os.environ.get("RECS_TABLE", "boardsite-recs"))),
        "reactions": DynamoTable(
            dynamo.Table(os.environ.get("REACTIONS_TABLE", "boardsite-reactions"))
        ),
        "notifications": DynamoTable(
            dynamo.Table(os.environ.get("NOTIFICATIONS_TABLE", "boardsite-notifications"))
        ),
        "settings": DynamoTable(
            dynamo.Table(os.environ.get("SETTINGS_TABLE", "boardsite-settings"))
        ),
    }


tables: dict = _make_tables()
