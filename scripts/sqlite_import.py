#!/usr/bin/env python3
"""Import JSON table dumps (produced by sqlite_export.py or export-tables.py)
into a selfhost SQLite DB.

Usage:
  python3 scripts/sqlite_import.py --db-path config/app/boardsite.db --in exports/2026-06-20/
"""
import argparse
import json
import sqlite3
from pathlib import Path

TABLES = (
    "users",
    "games",
    "results",
    "posts",
    "recs",
    "reactions",
    "notifications",
    "settings",
)


def import_tables(db_path: str, data: dict[str, list[dict]]) -> None:
    unknown = set(data) - set(TABLES)
    if unknown:
        raise ValueError(f"Unknown table(s) in import data: {sorted(unknown)}")

    conn = sqlite3.connect(db_path, isolation_level=None)
    try:
        for table in TABLES:
            conn.execute(
                f"CREATE TABLE IF NOT EXISTS {table} (pk TEXT PRIMARY KEY, data TEXT NOT NULL)"
            )
        conn.execute("BEGIN IMMEDIATE")
        try:
            for table, items in data.items():
                for item in items:
                    conn.execute(
                        f"INSERT INTO {table} (pk, data) VALUES (?, ?) "
                        "ON CONFLICT(pk) DO UPDATE SET data = excluded.data",
                        (item["pk"], json.dumps(item)),
                    )
            conn.execute("COMMIT")
        except Exception:
            conn.execute("ROLLBACK")
            raise
    finally:
        conn.close()


def main(argv: list[str] | None = None) -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--db-path", default="config/app/boardsite.db")
    parser.add_argument(
        "--in",
        dest="in_dir",
        required=True,
        help="dir containing <table>.json (sqlite_export.py) or boardsite-<table>*.json (export-tables.py) files",
    )
    args = parser.parse_args(argv)

    in_dir = Path(args.in_dir)
    data = {}
    for table in TABLES:
        path = in_dir / f"{table}.json"
        if not path.exists():
            # Fall back to export-tables.py's naming: boardsite-{table}.json
            # or boardsite-{table}-dev.json (cloud->selfhost migration path).
            matches = sorted(in_dir.glob(f"boardsite-{table}*.json"))
            path = matches[0] if matches else path
        if path.exists():
            data[table] = json.loads(path.read_text())

    import_tables(args.db_path, data)
    for table, items in data.items():
        print(f"{table}: imported {len(items)} items")


if __name__ == "__main__":
    main()
