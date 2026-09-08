---
title: Backups & upgrades
description: Back up, restore, upgrade and remove the self-hosted stack.
sidebar:
  order: 5
---

Runtime data lives in `./config/` on the host — no Docker volume commands needed. Stop the
app while you copy it: SQLite runs in WAL mode, so a copy taken mid-write can be
inconsistent.

```bash
docker compose stop
tar czf app-data.tar.gz config/app
docker compose start
```

The archive contains the database (every password hash) and `.jwt_secret` (mints a valid
session for any user). Treat it like a password: encrypt it or keep it off the box.

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

The script tars `config/app` as-is and does not stop the app itself, so wrap it in a
nightly crontab entry that does (a second or two of downtime at 03:00):

```
0 3 * * * cd /path/to/mc-gamertime && docker compose stop && ./scripts/backup-selfhost.sh --dest /path/to/backups --keep 14; docker compose start
```

## Upgrading

Image tags: `latest` and `X.Y.Z` follow releases; `main` is the edge build from every
commit. Take a backup, then:

```bash
docker compose pull
docker compose up -d
docker compose logs -f mc-gamertime   # until "Application startup complete"
```

Schema migrations run automatically on boot (`scripts/migrate-sqlite.py` in the
entrypoint) and are skipped once applied, so re-running is harmless. Before a major
upgrade, read the [release notes](/self-hosting/release-notes/): anything that reshapes
stored data is listed under a **BREAKING CHANGES** heading.

To roll back, pin the previous tag in `docker-compose.yml`
(`image: ghcr.io/strandgaard96/mc-gamertime:X.Y.Z`), restore the backup you took, and
`docker compose up -d`. Migrations are one-way; don't run a newer image against a
database and then downgrade without restoring.

## Removing the stack

```bash
docker compose down
docker image rm ghcr.io/strandgaard96/mc-gamertime
rm -rf config/          # all data, including the JWT secret — take a backup first
```

`docker compose down -v` does not touch `config/`; bind mounts are never deleted by `-v`.

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
