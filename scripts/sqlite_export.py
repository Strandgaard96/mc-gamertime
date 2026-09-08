#!/usr/bin/env python3
"""Export all 8 SQLite tables (selfhost) to JSON files.

Usage:
  python3 scripts/sqlite_export.py                      # config/app/boardsite.db -> exports/YYYY-MM-DD/
  python3 scripts/sqlite_export.py --db-path /data/boardsite.db --out /tmp/out
"""

import argparse
import json
import sqlite3
from datetime import date
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


def export_tables(db_path: str) -> dict[str, list[dict]]:
    conn = sqlite3.connect(db_path)
    try:
        result: dict[str, list[dict]] = {}
        for table in TABLES:
            try:
                rows = conn.execute(f"SELECT data FROM {table}").fetchall()
                result[table] = [json.loads(row[0]) for row in rows]
            except sqlite3.OperationalError as exc:
                if "no such table" not in str(exc):
                    # Something other than a missing table (e.g. a locked
                    # database) — must not be silently swallowed as "empty".
                    raise
                # Table doesn't exist yet (never been instantiated)
                result[table] = []
        return result
    finally:
        conn.close()


def main(argv: list[str] | None = None) -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--db-path", default="config/app/boardsite.db")
    parser.add_argument(
        "--out", default=None, help="output dir (default: exports/YYYY-MM-DD)"
    )
    args = parser.parse_args(argv)

    stamp = date.today().isoformat()
    out_dir = Path(args.out) if args.out else Path("exports") / stamp
    out_dir.mkdir(parents=True, exist_ok=True)

    data = export_tables(args.db_path)
    for table, items in data.items():
        path = out_dir / f"{table}.json"
        path.write_text(json.dumps(items, indent=2))
        print(f"{table}: {len(items)} items -> {path}")


if __name__ == "__main__":
    main()
