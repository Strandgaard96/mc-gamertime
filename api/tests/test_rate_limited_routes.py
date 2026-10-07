"""slowapi with headers_enabled=True injects X-RateLimit-* headers into the
route's `response: Response` parameter. A @limiter.limit route without one
raises at request time (slowapi cannot find a Response to decorate), and only
on the rate-limited routes, so it is easy to miss. Check every one statically.
"""

from __future__ import annotations

import importlib
import inspect

from starlette.responses import Response

from lib.rate_limit import limiter


def _rate_limited_endpoints():
    import main  # noqa: F401  (registers every route, and with it every limit)

    names = set(limiter._route_limits) | set(limiter._dynamic_route_limits)
    endpoints = []
    for name in sorted(names):
        module, func = name.rsplit(".", 1)
        endpoints.append(getattr(importlib.import_module(module), func))
    return endpoints


def test_rate_limited_routes_are_found():
    # Guards the test itself: if discovery breaks, the check below would pass
    # vacuously.
    assert len(_rate_limited_endpoints()) >= 6


def test_every_rate_limited_route_declares_a_response_parameter():
    missing = []
    for fn in _rate_limited_endpoints():
        params = inspect.signature(inspect.unwrap(fn)).parameters
        if not any(p.annotation in (Response, "Response") for p in params.values()):
            missing.append(f"{fn.__module__}.{fn.__name__}")
    assert not missing, f"@limiter.limit routes without `response: Response`: {missing}"
