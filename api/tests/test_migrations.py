import sqlite3

import pytest

from lib.db.migrations import run_migrations


def test_fresh_db_with_no_migrations_returns_version_0(tmp_path):
    db_path = str(tmp_path / "test.db")
    assert run_migrations(db_path, migrations=[]) == 0


def test_applies_pending_migration_and_records_version(tmp_path):
    db_path = str(tmp_path / "test.db")
    calls = []

    def add_widgets_table(conn):
        calls.append("add_widgets_table")
        conn.execute("CREATE TABLE widgets (pk TEXT PRIMARY KEY)")

    version = run_migrations(db_path, migrations=[(1, add_widgets_table)])

    assert version == 1
    assert calls == ["add_widgets_table"]
    conn = sqlite3.connect(db_path)
    tables = {row[0] for row in conn.execute("SELECT name FROM sqlite_master WHERE type='table'")}
    conn.close()
    assert "widgets" in tables


def test_already_applied_migration_does_not_run_again(tmp_path):
    db_path = str(tmp_path / "test.db")
    calls = []

    def add_widgets_table(conn):
        calls.append("add_widgets_table")
        conn.execute("CREATE TABLE widgets (pk TEXT PRIMARY KEY)")

    run_migrations(db_path, migrations=[(1, add_widgets_table)])
    run_migrations(db_path, migrations=[(1, add_widgets_table)])

    assert calls == ["add_widgets_table"]


def test_failed_migration_rolls_back_and_does_not_advance_version(tmp_path):
    db_path = str(tmp_path / "test.db")

    def broken_migration(conn):
        conn.execute("CREATE TABLE widgets (pk TEXT PRIMARY KEY)")
        raise RuntimeError("boom")

    with pytest.raises(RuntimeError):
        run_migrations(db_path, migrations=[(1, broken_migration)])

    conn = sqlite3.connect(db_path)
    tables = {row[0] for row in conn.execute("SELECT name FROM sqlite_master WHERE type='table'")}
    version_row = conn.execute("SELECT version FROM _schema_version").fetchone()
    conn.close()
    assert "widgets" not in tables
    assert version_row[0] == 0


def test_runs_multiple_pending_migrations_in_order(tmp_path):
    db_path = str(tmp_path / "test.db")
    order = []

    version = run_migrations(
        db_path,
        migrations=[
            (1, lambda conn: order.append(1)),
            (2, lambda conn: order.append(2)),
        ],
    )

    assert version == 2
    assert order == [1, 2]


def test_second_run_with_a_newly_added_migration_only_runs_the_new_one(tmp_path):
    db_path = str(tmp_path / "test.db")
    calls = []

    run_migrations(db_path, migrations=[(1, lambda conn: calls.append(1))])
    run_migrations(
        db_path,
        migrations=[(1, lambda conn: calls.append(1)), (2, lambda conn: calls.append(2))],
    )

    assert calls == [1, 2]


def test_data_outside_schema_version_table_is_untouched_by_a_noop_run(tmp_path):
    db_path = str(tmp_path / "test.db")
    conn = sqlite3.connect(db_path)
    conn.execute("CREATE TABLE games (pk TEXT PRIMARY KEY, data TEXT NOT NULL)")
    conn.execute("INSERT INTO games VALUES ('01GAME', '{}')")
    conn.commit()
    conn.close()

    run_migrations(db_path, migrations=[])

    conn = sqlite3.connect(db_path)
    row = conn.execute("SELECT data FROM games WHERE pk = '01GAME'").fetchone()
    conn.close()
    assert row == ("{}",)
