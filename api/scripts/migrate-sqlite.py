#!/usr/bin/env python3
"""Apply pending SQLite schema migrations (DB_BACKEND=sqlite only).

Run automatically by docker/entrypoint.sh before the app starts. Safe to
run on every boot — migrations already recorded in `_schema_version` are
skipped, so this is a no-op once a deployment is up to date.
"""

import os
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from lib.db.migrations import MIGRATIONS, run_migrations  # noqa: E402

if __name__ == "__main__":
    db_path = os.environ.get("SQLITE_DB_PATH", "/data/boardsite.db")
    version = run_migrations(db_path, MIGRATIONS)
    print(f"SQLite schema at version {version} ({db_path})")
