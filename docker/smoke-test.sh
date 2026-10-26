#!/bin/sh
# Boot an image the way a fresh self-hoster would and fail on any startup
# problem. Shared by ci.yml's Docker build (PRs) and publish.yml (before any
# push to GHCR), so the two gates can't drift apart.
#
# Usage: docker/smoke-test.sh <image>
#
# Checks, in order:
#   1. HEALTHCHECK reaches `healthy` (/api/health 503s if _initialize() failed)
#   2. GET / serves the SPA (a missing web build still passes /api/health)
#   3. the container logs hold no traceback and no ERROR/CRITICAL line — a
#      background failure can leave every endpoint answering 200
set -eu

image="$1"
name=smoke
port=4263

cleanup() { docker rm -f "$name" >/dev/null 2>&1 || true; }
trap cleanup EXIT

fail() {
    echo "::error::$1"
    echo "--- docker logs $name ---"
    docker logs "$name" 2>&1 || true
    exit 1
}

docker run -d --name "$name" -p "127.0.0.1:$port:$port" \
    -e ADMIN_USERNAME=smoke -e ADMIN_PASSWORD=smoke-test-password \
    "$image" >/dev/null

status=starting
for _ in $(seq 30); do
    status=$(docker inspect -f '{{.State.Health.Status}}' "$name")
    [ "$status" = healthy ] && break
    [ "$status" = unhealthy ] && break
    sleep 2
done
[ "$status" = healthy ] || fail "container never became healthy (status: $status)"

curl -fsS "http://127.0.0.1:$port/api/health" >/dev/null ||
    fail "/api/health did not return 2xx"
curl -fsS "http://127.0.0.1:$port/" | grep -q 'id="root"' ||
    fail "/ did not serve the web app's index.html"

# Matches app log lines ("ERROR name: msg", main.py's basicConfig format),
# uvicorn's ("ERROR:    msg") and any Python traceback.
if docker logs "$name" 2>&1 | grep -Eq '^(ERROR|CRITICAL)[: ]|Traceback \(most recent call last\)'; then
    fail "errors in container logs"
fi

echo "Smoke test passed: healthy, SPA served, clean logs"
docker logs "$name" 2>&1
