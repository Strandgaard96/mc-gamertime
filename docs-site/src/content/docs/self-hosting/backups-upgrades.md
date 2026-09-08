---
title: Backups
description: Back up and restore MC GamerTime's data.
sidebar:
  order: 5
---

Runtime data lives in `./config/` on the host — no Docker volume commands needed:
```bash
tar czf app-data.tar.gz config/app
```

To restore, stop the stack, extract the archive into the same path, then restart:

```bash
docker compose down
tar xzf app-data.tar.gz
docker compose up -d
```

## Automating backups

Run the bundled script on a schedule instead of backing up by hand:

```bash
./scripts/backup-selfhost.sh --dest /path/to/backups --keep 14
```

Add a crontab entry to run it nightly, keeping 14 days of backups:

```
0 3 * * * cd /path/to/mc-gamertime && ./scripts/backup-selfhost.sh --dest /path/to/backups --keep 14
```

## Exporting and importing table data

For partial recovery or moving data between a selfhosted instance and the cloud
deployment, dump individual tables as JSON instead of restoring a whole backup:

```bash
python3 scripts/sqlite_export.py --db-path config/app/boardsite.db --out exports/
python3 scripts/sqlite_import.py --db-path config/app/boardsite.db --in exports/2026-06-20/
```

Both scripts use only the Python standard library — no `uv` or virtualenv needed.
Import validates table names before writing anything; a bad input file leaves the
database untouched.

Stop the stack first (`docker compose down`) before running either script against a live
database. The app holds a 30s busy timeout on its own connections, but these scripts don't —
running `sqlite_import.py` against a writing app can fail with "database is locked" after a
few seconds, and `sqlite_export.py` could capture a partially-consistent snapshot.
