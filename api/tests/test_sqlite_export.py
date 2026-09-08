import importlib.util
import json
import sqlite3
import sys
from pathlib import Path

import pytest

from lib.db.sqlite_backend import SqliteTable

SCRIPT_PATH = Path(__file__).resolve().parents[2] / "scripts" / "sqlite_export.py"
spec = importlib.util.spec_from_file_location("sqlite_export", SCRIPT_PATH)
assert spec is not None
assert spec.loader is not None
sqlite_export = importlib.util.module_from_spec(spec)
sys.modules["sqlite_export"] = sqlite_export
spec.loader.exec_module(sqlite_export)


def test_export_tables_returns_all_eight_tables_with_items(tmp_path):
    db_path = str(tmp_path / "test.db")
    SqliteTable(db_path, "games").put_item(Item={"pk": "01GAME", "name": "Wingspan"})
    SqliteTable(db_path, "users").put_item(Item={"pk": "admin", "role": "admin"})

    result = sqlite_export.export_tables(db_path)

    assert set(result) == {
        "users",
        "games",
        "results",
        "posts",
        "recs",
        "reactions",
        "notifications",
        "settings",
    }
    assert result["games"] == [{"pk": "01GAME", "name": "Wingspan"}]
    assert result["users"] == [{"pk": "admin", "role": "admin"}]
    assert result["results"] == []


def test_main_writes_one_json_file_per_table(tmp_path):
    db_path = str(tmp_path / "test.db")
    SqliteTable(db_path, "games").put_item(Item={"pk": "01GAME", "name": "Wingspan"})
    out_dir = tmp_path / "out"

    sqlite_export.main(["--db-path", db_path, "--out", str(out_dir)])

    games_file = out_dir / "games.json"
    assert games_file.exists()
    assert json.loads(games_file.read_text()) == [{"pk": "01GAME", "name": "Wingspan"}]
    assert (out_dir / "results.json").exists()


def test_export_tables_propagates_lock_error_instead_of_returning_empty(tmp_path):
    """A real 'database is locked' OperationalError (not a missing table)
    must propagate, not be swallowed into an empty list — otherwise a busy
    table could silently export as zero rows with no error or warning.
    """
    db_path = str(tmp_path / "test.db")
    # Create the table and seed a row so an empty-list result would be wrong.
    SqliteTable(db_path, "games").put_item(Item={"pk": "01GAME", "name": "Wingspan"})

    # SqliteTable leaves the db file in WAL mode, which lets readers proceed
    # even while a writer holds an uncommitted transaction. Force the
    # locker connection back to rollback-journal mode before taking an
    # EXCLUSIVE lock so a concurrent reader (export_tables' plain
    # sqlite3.connect) genuinely hits "database is locked".
    locker = sqlite3.connect(db_path)
    locker.execute("PRAGMA journal_mode=DELETE")
    locker.execute("BEGIN EXCLUSIVE")
    try:
        with pytest.raises(sqlite3.OperationalError, match="locked"):
            sqlite_export.export_tables(db_path)
    finally:
        locker.execute("ROLLBACK")
        locker.close()
