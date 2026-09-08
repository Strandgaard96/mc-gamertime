from fastapi import FastAPI, Request
from fastapi.testclient import TestClient
from uvicorn.middleware.proxy_headers import ProxyHeadersMiddleware

# Mirrors docker/entrypoint.sh's --forwarded-allow-ips default exactly. If you
# change one, change the other — this list is what lets the rate limiter
# (lib/rate_limit.py's get_remote_address, which reads request.client.host) see the
# real visitor instead of the proxy, for every reverse-proxy setup documented in
# docs-site/.../self-hosting/https.mdx (nginx-on-host via Docker's NAT'd bridge
# gateway, Traefik on the compose network, Tailscale serve, or a dedicated LAN box).
TRUSTED_PROXY_RANGES = [
    "127.0.0.1",
    "::1",
    "10.0.0.0/8",
    "172.16.0.0/12",
    "192.168.0.0/16",
]


def _whoami_app() -> FastAPI:
    app = FastAPI()

    @app.get("/whoami")
    def whoami(request: Request):
        return {"client": request.client.host if request.client else None}

    return app


def test_forwarded_for_honored_from_trusted_docker_bridge_gateway():
    """nginx-on-host reaches the container through Docker's published-port NAT, so
    the real TCP peer the app sees is the bridge gateway (172.17.0.1 is the default
    on a stock Docker install), not the real visitor or nginx's own address."""
    wrapped = ProxyHeadersMiddleware(_whoami_app(), trusted_hosts=TRUSTED_PROXY_RANGES)
    client = TestClient(wrapped, client=("172.17.0.1", 40000))

    resp = client.get("/whoami", headers={"X-Forwarded-For": "203.0.113.7"})

    assert resp.json() == {"client": "203.0.113.7"}


def test_forwarded_for_honored_from_trusted_lan_reverse_proxy():
    """A dedicated reverse-proxy box elsewhere on the self-hoster's LAN is also a
    documented topology; its IP falls in the 192.168.0.0/16 private range."""
    wrapped = ProxyHeadersMiddleware(_whoami_app(), trusted_hosts=TRUSTED_PROXY_RANGES)
    client = TestClient(wrapped, client=("192.168.1.50", 40000))

    resp = client.get("/whoami", headers={"X-Forwarded-For": "203.0.113.7"})

    assert resp.json() == {"client": "203.0.113.7"}


def test_forwarded_for_ignored_when_exposed_directly_to_internet():
    """If a self-hoster forwards the app's port straight to the internet against the
    docs' warning, the real peer is the attacker's own public IP, which must NOT be
    in the trusted ranges -- otherwise the attacker could forge X-Forwarded-For to
    bypass per-IP rate limiting entirely."""
    wrapped = ProxyHeadersMiddleware(_whoami_app(), trusted_hosts=TRUSTED_PROXY_RANGES)
    client = TestClient(wrapped, client=("203.0.113.7", 40000))

    resp = client.get("/whoami", headers={"X-Forwarded-For": "9.9.9.9"})

    assert resp.json() == {"client": "203.0.113.7"}
