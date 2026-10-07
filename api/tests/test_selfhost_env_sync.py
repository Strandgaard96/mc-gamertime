"""Every self-host setting in .env.example must reach the container.

docker compose auto-loads .env, but a variable only reaches the app if the
mc-gamertime service's `environment:` block passes it through. A setting that
is documented (the docs page embeds .env.example verbatim) but not passed
through is silently ignored.
"""

from __future__ import annotations

import re
from pathlib import Path

_ROOT = Path(__file__).resolve().parents[2]

# Read by docker compose itself (port binding, user mapping), never by the app.
_COMPOSE_ONLY = {"APP_BIND", "APP_PORT", "PUID", "PGID"}


def _env_example_keys() -> set[str]:
    text = (_ROOT / ".env.example").read_text()
    return set(re.findall(r"^#?\s*([A-Z][A-Z0-9_]*)=", text, re.M))


def _compose_passthrough_keys() -> set[str]:
    text = (_ROOT / "docker-compose.yml").read_text()
    return set(re.findall(r"^\s+([A-Z][A-Z0-9_]*):\s*\$\{\1[:}-]", text, re.M))


def test_every_env_example_setting_is_passed_to_the_container():
    missing = _env_example_keys() - _COMPOSE_ONLY - _compose_passthrough_keys()
    assert not missing, (
        f"In .env.example but not passed through docker-compose.yml: {sorted(missing)}. "
        "Add `NAME: ${NAME:-}` under mc-gamertime.environment."
    )


def test_every_passthrough_is_documented_in_env_example():
    undocumented = _compose_passthrough_keys() - _env_example_keys()
    assert not undocumented, (
        f"Passed through compose but missing from .env.example: {sorted(undocumented)}"
    )


def test_compose_only_settings_stay_out_of_the_app_environment():
    leaked = _compose_passthrough_keys() & _COMPOSE_ONLY
    assert not leaked, f"{sorted(leaked)} are read by docker compose, not the app"
