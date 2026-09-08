import os

from slowapi import Limiter
from slowapi.util import get_remote_address
from starlette.requests import Request

# Number of trusted reverse-proxy hops that append to X-Forwarded-For between the
# real client and this app. A client can only *prepend* (spoof) left-most XFF
# entries, so we only trust entries counted from the RIGHT — never the left-most,
# which is attacker-controlled and would let anyone rotate their rate-limit key.
#
#   0 (default) → don't trust XFF at all; use the socket/platform source IP. Safe
#                 everywhere: no spoofable bypass. Selfhost keeps this and relies
#                 on uvicorn --proxy-headers to fix request.client.host instead.
#   N > 0       → cloud (CloudFront → API Gateway): set N so parts[-N] lands on
#                 the viewer IP that CloudFront appended. Verify against a real
#                 request log before trusting a value.
_TRUSTED_PROXY_HOPS = int(os.environ.get("TRUSTED_PROXY_HOPS", "0"))


def client_ip(request: Request) -> str:
    """Real client IP for rate-limit keying and security logs.

    Only consults X-Forwarded-For when TRUSTED_PROXY_HOPS is configured, and then
    only from the right (infra-appended, unspoofable). Otherwise falls back to the
    platform source IP so a forged XFF can never move the key.
    """
    if _TRUSTED_PROXY_HOPS > 0:
        parts = [
            p.strip() for p in request.headers.get("x-forwarded-for", "").split(",") if p.strip()
        ]
        idx = len(parts) - _TRUSTED_PROXY_HOPS
        if 0 <= idx < len(parts):
            return parts[idx]
    return get_remote_address(request)


limiter = Limiter(key_func=client_ip, headers_enabled=True)
