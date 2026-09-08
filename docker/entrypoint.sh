#!/bin/sh
set -e

# JWT_SECRET is auto-generated on first boot and persisted to the /data
# volume — matches the Django SECRET_KEY / *arr API-key convention. Never
# logged, never served over HTTP (file mode 0600, /data is not under
# STATIC_DIR or the /storage proxy's path).
SECRET_FILE=/data/.jwt_secret
if [ ! -f "$SECRET_FILE" ]; then
    umask 077
    openssl rand -hex 32 > "$SECRET_FILE"
fi
JWT_SECRET="$(cat "$SECRET_FILE")"
export JWT_SECRET

# SQLite schema creation (lib/db/sqlite_backend.py) and storage directory
# creation (lib/storage.py::LocalFsClient) both happen lazily in-process on
# first use — no separate bootstrap scripts needed.

if [ "$DB_BACKEND" = "sqlite" ]; then
    python3 scripts/migrate-sqlite.py
fi

# --proxy-headers is already uvicorn's default, but pinned explicitly here for
# clarity. --forwarded-allow-ips must match api/tests/test_proxy_headers.py's
# TRUSTED_PROXY_RANGES — both lists exist to let the app see each real visitor's IP
# (for rate limiting) when run behind any of the reverse proxies documented in
# docs-site/.../self-hosting/https.mdx, while still ignoring forged
# X-Forwarded-For from a genuine direct-internet connection (CLAUDE.md's
# "your LAN is trusted" selfhost threat model — a real attacker's TCP source IP is
# never a private range unless they're already inside it).
exec uvicorn main:app --host 0.0.0.0 --port 4263 \
    --proxy-headers \
    --forwarded-allow-ips "${FORWARDED_ALLOW_IPS:-127.0.0.1,::1,10.0.0.0/8,172.16.0.0/12,192.168.0.0/16}"
