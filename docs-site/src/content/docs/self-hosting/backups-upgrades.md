---
title: Backups & Upgrades
description: Back up volumes and upgrade MC GamerTime to a new version.
sidebar:
  order: 7
---

## Backups

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

### Automating backups

Run the bundled script on a schedule instead of backing up by hand:

```bash
./scripts/backup-selfhost.sh --dest /path/to/backups --keep 14
```

Add a crontab entry to run it nightly, keeping 14 days of backups:

```
0 3 * * * cd /path/to/mc-gamertime && ./scripts/backup-selfhost.sh --dest /path/to/backups --keep 14
```

**`docker compose down -v`** has no effect on data — bind-mounted directories are not
deleted by `-v`. To fully wipe all data, delete the `config/` directory manually after
bringing the stack down.

### Exporting and importing table data

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

## Upgrading

```bash
docker compose pull
docker compose up -d
```

### Breaking change: the default port moved to 4263

Older versions published `8080:8000`. The container now listens on **4263** and Compose
publishes **`4263:4263`**. After upgrading:

- Reach the app at `http://localhost:4263` — update bookmarks.
- Point any reverse proxy upstream at port 4263 (`proxy_pass http://127.0.0.1:4263;` for
  nginx, `loadbalancer.server.port=4263` for Traefik).
- If you had pinned the old mapping in your own `docker-compose.yml`, replace `8080:8000`
  with `4263:4263`, or set `APP_PORT=8080` in `.env` to keep the old host port while the
  container moves to 4263.

8080 was dropped because it collides with almost every other self-hosted app; 4263 is
unclaimed (and spells GAME on a phone keypad).

## Upgrading from a pre-SQLite version (rare)

Only relevant if you're upgrading from a very old install that still has `config/dynamodb`
and `config/seaweed` directories — those versions used `dynamodb-local` + `seaweedfs`
containers for storage. This version replaces both with an embedded SQLite database and
local filesystem storage — there is no migration path; existing selfhost data does not
carry forward.

```bash
# 1. Back up config/ first if you want to keep anything (optional — the old
#    format isn't read by the new version)
tar czf old-data-backup.tar.gz config/

# 2. Stop the stack and remove the old data directories
docker compose down
rm -rf config/dynamodb config/seaweed

# 3. Pull and start the new version
docker compose pull
docker compose up -d

# 4. Re-bootstrap
docker compose exec app python3 scripts/create-user.py --username admin --display-name "Admin" --role admin --password <your-password>
```
