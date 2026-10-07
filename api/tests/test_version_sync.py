"""Every place that carries the release version must agree.

release-please bumps api/pyproject.toml and web/package.json via `extra-files`
and records the release in .release-please-manifest.json; uv.lock carries the
project version too and is only rewritten by `uv lock`. If any of these drift,
the release PR ships mismatched versions (or `uv sync --locked` fails in CI).
"""

import json
import tomllib
from pathlib import Path

REPO = Path(__file__).resolve().parents[2]


def _versions() -> dict[str, str]:
    pyproject = tomllib.loads((REPO / "api" / "pyproject.toml").read_text())
    lock = tomllib.loads((REPO / "api" / "uv.lock").read_text())
    lock_version = next(
        p["version"] for p in lock["package"] if p["name"] == pyproject["project"]["name"]
    )
    return {
        "api/pyproject.toml [project].version": pyproject["project"]["version"],
        "api/uv.lock root package version": lock_version,
        "web/package.json version": json.loads((REPO / "web" / "package.json").read_text())[
            "version"
        ],
        '.release-please-manifest.json "."': json.loads(
            (REPO / ".release-please-manifest.json").read_text()
        )["."],
    }


def test_versions_match() -> None:
    versions = _versions()
    assert len(set(versions.values())) == 1, "release versions disagree:\n" + "\n".join(
        f"  {where}: {version}" for where, version in versions.items()
    )
