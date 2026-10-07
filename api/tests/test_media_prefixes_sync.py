"""The uploaded-media prefixes live in two languages and must agree.

App side: MEDIA_PREFIXES in routes/storage.py (the proxy allowlist, and the
media_router mounts in main.py). Infra side: local.media_prefixes in
infra/main.tf (CloudFront behaviours, Lambda S3 IAM, the S3 Deny). A prefix in
one but not the other is either unreadable (403 on every upload/read) or
world-readable straight from S3.
"""

from __future__ import annotations

import re
from pathlib import Path

from routes.storage import MEDIA_PREFIXES
from tests.conftest import route_paths

_MAIN_TF = Path(__file__).resolve().parents[2] / "infra" / "main.tf"


def _terraform_media_prefixes() -> list[str]:
    match = re.search(r"^\s*media_prefixes\s*=\s*\[([^\]]*)\]", _MAIN_TF.read_text(), re.M)
    assert match, "local.media_prefixes not found in infra/main.tf"
    return re.findall(r'"([^"]+)"', match.group(1))


def test_terraform_and_app_media_prefixes_match():
    assert sorted(_terraform_media_prefixes()) == sorted(MEDIA_PREFIXES)


def test_every_media_prefix_is_mounted():
    from main import app

    paths = route_paths(app)
    for prefix in MEDIA_PREFIXES:
        assert any(p.startswith(f"/{prefix}/") for p in paths), f"/{prefix} not mounted"
