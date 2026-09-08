"""The table interface both backends implement.

`_make_tables()` hands lib/db/*.py either a `DynamoTable` or a `SqliteTable`
depending on DB_BACKEND, and every caller from that point on is written against
whichever it got. This Protocol is the contract between them; the conformance
tests in tests/test_db_contract.py assert that both classes satisfy it and that
their signatures have not drifted apart.
"""

from __future__ import annotations

from typing import Protocol, runtime_checkable


@runtime_checkable
class Table(Protocol):
    def get_item(self, *, Key: dict) -> dict: ...

    def put_item(self, *, Item: dict) -> None: ...

    def delete_item(self, *, Key: dict) -> None: ...

    def scan(self, **kwargs) -> dict: ...

    def add_to_set(self, pk: str, field: str, value) -> None: ...

    def remove_from_set(self, pk: str, field: str, value) -> None: ...

    def increment_with_timestamp(
        self, pk: str, counter_field: str, timestamp_field: str, timestamp_value
    ) -> None: ...
