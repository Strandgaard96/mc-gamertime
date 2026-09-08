---
title: Troubleshooting
description: Common issues and fixes for the self-hosted Docker Compose stack.
sidebar:
  order: 6
---

## App won't start / restarts in a loop

Run `docker compose logs mc-gamertime`. If the last line is

```
/entrypoint.sh: 11: cannot create /data/.jwt_secret: Permission denied
```

the bind-mounted `config/app/` is not writable by the user the container runs as. Check
its owner with `ls -ld config/app` and set `PUID`/`PGID` in `.env` to match (`id -u` /
`id -g`), then `docker compose up -d` — the init container re-applies the ownership on
every start.

## Every request returns 503, but the container is "healthy"

```bash
curl -i http://localhost:4263/
# HTTP/1.1 503 Service Unavailable
# {"detail":"Service unavailable"}
```

The database has no users and no `ADMIN_USERNAME`/`ADMIN_PASSWORD` was set, so startup
aborts and every request — the login page included — is refused. Docker still reports the
container `healthy`, because the healthcheck only opens a TCP connection to port 4263; it
never asks for a page.

Confirm it in the logs, then create the first admin:

```bash
docker compose logs mc-gamertime | grep "No users found"
docker compose exec mc-gamertime python3 scripts/create-user.py \
  --username admin --display-name "Admin" --role admin --password <your-password>
```

The next request succeeds; no restart needed. Setting only one of `ADMIN_USERNAME` /
`ADMIN_PASSWORD` produces the same 503 by a different route — it is a hard startup error.

## Images / avatars 404 via /storage/...

Only the `avatars/`, `blog-images/`, and `game-images/` prefixes are served by the proxy. Check that `config/app/storage/` exists and is writable inside the container:

```bash
docker compose exec mc-gamertime ls -la /data/storage
```

## Logs

```bash
docker compose logs -f            # all services, follow
docker compose logs mc-gamertime           # app only
docker compose ps                 # health status of all services
```
