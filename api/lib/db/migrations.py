"""SQLite schema migration framework for DB_BACKEND=sqlite (selfhost).

`MIGRATIONS` is an ordered list of `(version, fn)` pairs. Each `fn` receives
an open `sqlite3.Connection` already inside a transaction and applies one
additive schema change (new table, new column — never a destructive one).
Migrations run once, at container boot (see `scripts/migrate-sqlite.py` and
`docker/entrypoint.sh`), tracked via the single-row `_schema_version` table.

Version numbers must be unique and strictly ascending in list order — this
module does not sort by version to detect or fix an out-of-order list, it
trusts the list as written.

This intentionally has no dependency on Alembic or any migration library:
the selfhost schema changes slowly enough that a tracked version number and
a list of plain functions is sufficient.
"""

from __future__ import annotations

import sqlite3
from collections.abc import Callable

# Example (when you need one):
#   def _add_archived_to_results(conn: sqlite3.Connection) -> None:
#       conn.execute("ALTER TABLE results ADD COLUMN archived INTEGER DEFAULT 0")
#
#   MIGRATIONS = [(1, _add_archived_to_results)]
MIGRATIONS: list[tuple[int, Callable[[sqlite3.Connection], None]]] = []


def run_migrations(
    db_path: str,
    migrations: list[tuple[int, Callable[[sqlite3.Connection], None]]] | None = None,
) -> int:
    if migrations is None:
        migrations = MIGRATIONS

    conn = sqlite3.connect(db_path, timeout=30, isolation_level=None)
    try:
        conn.execute("PRAGMA journal_mode=WAL")
        conn.execute("PRAGMA busy_timeout=30000")
        conn.execute("CREATE TABLE IF NOT EXISTS _schema_version (version INTEGER NOT NULL)")
        row = conn.execute("SELECT version FROM _schema_version").fetchone()
        if row is None:
            conn.execute("INSERT INTO _schema_version (version) VALUES (0)")
            current = 0
        else:
            current = row[0]

        for version, apply in migrations:
            if version <= current:
                continue
            conn.execute("BEGIN IMMEDIATE")
            try:
                apply(conn)
            except Exception:
                conn.execute("ROLLBACK")
                raise
            conn.execute("UPDATE _schema_version SET version = ?", (version,))
            conn.execute("COMMIT")
            current = version

        return current
    finally:
        conn.close()
