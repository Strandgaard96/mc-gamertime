import time

import boto3
import pytest
from ulid import ULID

import lib.storage as storage
from lib.auth import _get_secret
from lib.storage import PHOTO_KEY_RE, build_upload, sign_photo_upload, verify_photo_upload


def test_make_s3_client_uses_real_aws_on_s3_backend(monkeypatch):
    # STORAGE_BACKEND=s3 is what infra/lambda.tf sets; without it the default is
    # the local filesystem (see test_make_s3_client_defaults_to_local_fs).
    monkeypatch.delenv("S3_ENDPOINT_URL", raising=False)
    monkeypatch.setenv("STORAGE_BACKEND", "s3")
    captured = {}

    def fake_client(service, **kwargs):
        captured.update(kwargs)
        return "client"

    monkeypatch.setattr(boto3, "client", fake_client)

    result = storage.make_s3_client()

    assert result == "client"
    assert "endpoint_url" not in captured
    assert "config" not in captured


def test_make_s3_client_with_endpoint_url_uses_path_style(monkeypatch):
    monkeypatch.setenv("S3_ENDPOINT_URL", "http://seaweedfs:8333")
    monkeypatch.setenv("S3_ACCESS_KEY", "admin")
    monkeypatch.setenv("S3_SECRET_KEY", "supersecret")
    captured = {}

    def fake_client(service, **kwargs):
        captured.update(kwargs)
        return "client"

    monkeypatch.setattr(boto3, "client", fake_client)

    storage.make_s3_client()

    assert captured["endpoint_url"] == "http://seaweedfs:8333"
    assert captured["aws_access_key_id"] == "admin"
    assert captured["aws_secret_access_key"] == "supersecret"
    assert captured["config"].s3["addressing_style"] == "path"


def test_get_object_base_url_ignores_cloudfront_url(monkeypatch):
    # Media is served by the app on every deployment, so the read URL must stay
    # same-origin: an absolute CloudFront URL would be cross-site against the
    # app's own domain and the SameSite=Strict session cookie would not be sent.
    monkeypatch.setenv("CLOUDFRONT_URL", "https://cdn.example.com")
    monkeypatch.setenv("S3_ENDPOINT_URL", "http://seaweedfs:8333")
    assert storage.get_object_base_url() == "/storage"


def test_get_object_base_url_is_relative_on_cloud(monkeypatch):
    monkeypatch.delenv("S3_ENDPOINT_URL", raising=False)
    monkeypatch.setenv("STORAGE_BACKEND", "s3")
    monkeypatch.setenv("CLOUDFRONT_URL", "https://cdn.example.com")
    assert storage.get_object_base_url() == ""


def test_get_object_base_url_falls_back_to_storage_proxy(monkeypatch):
    monkeypatch.delenv("CLOUDFRONT_URL", raising=False)
    monkeypatch.setenv("S3_ENDPOINT_URL", "http://seaweedfs:8333")
    assert storage.get_object_base_url() == "/storage"


def test_get_object_base_url_empty_on_s3_backend_without_cloudfront(monkeypatch):
    monkeypatch.delenv("CLOUDFRONT_URL", raising=False)
    monkeypatch.delenv("S3_ENDPOINT_URL", raising=False)
    monkeypatch.setenv("STORAGE_BACKEND", "s3")
    assert storage.get_object_base_url() == ""


def test_make_s3_client_defaults_to_local_fs(monkeypatch, tmp_path):
    # No storage configuration at all is the selfhost default.
    from lib.storage import LocalFsClient

    monkeypatch.delenv("S3_ENDPOINT_URL", raising=False)
    monkeypatch.delenv("STORAGE_BACKEND", raising=False)
    monkeypatch.setenv("LOCAL_STORAGE_DIR", str(tmp_path))

    assert isinstance(storage.make_s3_client(), LocalFsClient)


def test_get_object_base_url_defaults_to_storage_proxy(monkeypatch):
    monkeypatch.delenv("CLOUDFRONT_URL", raising=False)
    monkeypatch.delenv("S3_ENDPOINT_URL", raising=False)
    monkeypatch.delenv("STORAGE_BACKEND", raising=False)
    assert storage.get_object_base_url() == "/storage"


def test_ext_by_content_type_maps_known_image_types():
    assert storage.EXT_BY_CONTENT_TYPE["image/png"] == "png"
    assert storage.EXT_BY_CONTENT_TYPE["image/jpeg"] == "jpg"


def test_make_s3_client_returns_local_fs_client_when_storage_backend_local(monkeypatch, tmp_path):
    from lib.storage import LocalFsClient

    monkeypatch.setenv("STORAGE_BACKEND", "local")
    monkeypatch.setenv("LOCAL_STORAGE_DIR", str(tmp_path))

    result = storage.make_s3_client()

    assert isinstance(result, LocalFsClient)


def test_get_object_base_url_storage_backend_local_without_s3_endpoint_url(monkeypatch):
    monkeypatch.delenv("CLOUDFRONT_URL", raising=False)
    monkeypatch.delenv("S3_ENDPOINT_URL", raising=False)
    monkeypatch.setenv("STORAGE_BACKEND", "local")
    assert storage.get_object_base_url() == "/storage"


def test_build_upload_url_presigns_with_prefix(monkeypatch):
    monkeypatch.delenv("S3_ENDPOINT_URL", raising=False)
    monkeypatch.setenv("STORAGE_BACKEND", "s3")
    captured = {}

    class FakeS3:
        def generate_presigned_url(self, op, Params, ExpiresIn):
            captured["key"] = Params["Key"]
            captured["bucket"] = Params["Bucket"]
            captured["has_length"] = "ContentLength" in Params
            return "https://example.com/presigned"

    upload_url, image_url = storage.build_upload_url(
        FakeS3(), "my-bucket", "https://cdn.example.com", "game-images", "image/png"
    )

    assert upload_url == "https://example.com/presigned"
    assert captured["bucket"] == "my-bucket"
    assert captured["key"].startswith("game-images/")
    assert captured["key"].endswith(".png")
    assert image_url == f"https://cdn.example.com/{captured['key']}"
    assert captured["has_length"] is False  # only photo uploads bind a size


def test_build_upload_url_selfhost_returns_same_url_for_both(monkeypatch):
    monkeypatch.setenv("S3_ENDPOINT_URL", "http://seaweedfs:8333")

    upload_url, image_url = storage.build_upload_url(
        None, "my-bucket", "/storage", "game-images", "image/png"
    )

    assert upload_url == image_url
    assert upload_url.startswith("/storage/game-images/")
    assert upload_url.endswith(".png")


def test_photo_key_re_accepts_valid_keys():
    ulid = str(ULID())
    for ext in ("webp", "jpg", "png"):
        assert PHOTO_KEY_RE.match(f"session-images/{ulid}.{ext}")


def test_photo_key_re_rejects_bad_keys():
    ulid = str(ULID())
    for key in (
        f"session-images/{ulid}.gif",
        f"session-images/{ulid}.jpeg",
        "session-images/../avatars/x.png",
        f"blog-images/{ulid}.png",
        f"session-images/{ulid}.png/extra",
        "session-images/short.png",
        f"session-images/{ulid}.png\n",
    ):
        assert not PHOTO_KEY_RE.match(key), key


def test_build_upload_returns_key_matching_urls(monkeypatch):
    monkeypatch.setenv("STORAGE_BACKEND", "local")
    upload_url, image_url, key = build_upload(
        None, "bucket", "/storage", "game-images", "image/webp"
    )
    assert image_url == f"/storage/{key}"
    assert upload_url == image_url
    assert key.startswith("game-images/")


# --- photo upload tokens (selfhost /storage proxy) ---

_KEY = f"session-images/{ULID()!s}.webp"


def _params(query: str) -> dict[str, str]:
    return dict(pair.split("=", 1) for pair in query.split("&"))


def test_upload_token_round_trip():
    q = sign_photo_upload(_KEY, 1234, secret="s3cret", now=1000)
    params = _params(q)
    assert set(params) == {"exp", "len", "sig"}
    assert params["exp"] == str(1000 + 300)
    assert params["len"] == "1234"
    assert verify_photo_upload(_KEY, params, secret="s3cret", now=1000) == 1234
    assert verify_photo_upload(_KEY, params, secret="s3cret", now=1300) == 1234


def test_upload_token_expired():
    params = _params(sign_photo_upload(_KEY, 1234, secret="s3cret", now=1000))
    assert verify_photo_upload(_KEY, params, secret="s3cret", now=1301) is None


def test_upload_token_tampered_fields_rejected():
    params = _params(sign_photo_upload(_KEY, 1234, secret="s3cret", now=1000))
    other_key = f"session-images/{ULID()!s}.webp"
    assert verify_photo_upload(other_key, params, secret="s3cret", now=1000) is None
    for field, value in (("len", "99999"), ("exp", "999999"), ("sig", "0" * 64)):
        bad = {**params, field: value}
        assert verify_photo_upload(_KEY, bad, secret="s3cret", now=1000) is None, field


def test_upload_token_wrong_secret_rejected():
    params = _params(sign_photo_upload(_KEY, 1234, secret="s3cret", now=1000))
    assert verify_photo_upload(_KEY, params, secret="other", now=1000) is None


def test_upload_token_missing_or_malformed_rejected():
    params = _params(sign_photo_upload(_KEY, 1234, secret="s3cret", now=1000))
    for field in ("exp", "len", "sig"):
        partial = {k: v for k, v in params.items() if k != field}
        assert verify_photo_upload(_KEY, partial, secret="s3cret", now=1000) is None, field
    assert verify_photo_upload(_KEY, {**params, "len": "abc"}, secret="s3cret", now=1000) is None


def test_build_upload_photo_selfhost_url_carries_token(monkeypatch):
    monkeypatch.setenv("STORAGE_BACKEND", "local")
    monkeypatch.delenv("S3_ENDPOINT_URL", raising=False)
    upload_url, image_url, key = build_upload(
        None, "bucket", "/storage", "session-images", "image/webp", content_length=4321
    )
    assert PHOTO_KEY_RE.match(key)
    assert image_url == f"/storage/{key}"
    path, query = upload_url.split("?", 1)
    assert path == image_url
    params = _params(query)
    assert params["len"] == "4321"
    assert verify_photo_upload(key, params, secret=_get_secret(), now=int(time.time())) == 4321


def test_build_upload_cloud_presign_binds_content_length(monkeypatch):
    monkeypatch.delenv("S3_ENDPOINT_URL", raising=False)
    monkeypatch.setenv("STORAGE_BACKEND", "s3")
    captured = {}

    class FakeS3:
        def generate_presigned_url(self, op, Params, ExpiresIn):
            captured.update(Params)
            return "https://example.com/upload"

    upload_url, _image_url, key = build_upload(
        FakeS3(), "bucket", "", "session-images", "image/webp", content_length=4321
    )
    assert upload_url == "https://example.com/upload"
    assert captured["ContentLength"] == 4321
    assert captured["Key"] == key


def test_build_upload_photo_selfhost_requires_length(monkeypatch):
    monkeypatch.setenv("STORAGE_BACKEND", "local")
    monkeypatch.delenv("S3_ENDPOINT_URL", raising=False)
    with pytest.raises(ValueError, match="content_length"):
        build_upload(None, "bucket", "/storage", "session-images", "image/webp")
