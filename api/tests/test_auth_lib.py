import pytest
from fastapi import HTTPException

from lib.auth import (
    AuthUser,
    decode_reset_token,
    decode_token,
    require_admin,
    require_auth,
    set_jwt_secret,
    sign_reset_token,
    sign_token,
)


def setup_function():
    set_jwt_secret("test-secret-key-long-enough-for-hs256")


def test_sign_and_decode_roundtrip():
    user = AuthUser(sub="alice", role="admin", displayName="Alice")
    token = sign_token(user)
    decoded = decode_token(token)
    assert decoded.sub == "alice"
    assert decoded.role == "admin"
    assert decoded.displayName == "Alice"


def test_decode_invalid_token_raises():
    from jose import JWTError

    with pytest.raises(JWTError):
        decode_token("not.a.valid.token")


def test_require_auth_no_cookie_raises_401():
    with pytest.raises(HTTPException) as exc_info:
        require_auth(token=None)
    assert exc_info.value.status_code == 401


def test_require_auth_invalid_token_raises_401():
    with pytest.raises(HTTPException) as exc_info:
        require_auth(token="bad.token.here")
    assert exc_info.value.status_code == 401


def test_require_admin_non_admin_raises_403():
    user = AuthUser(sub="bob", role="readonly", displayName="Bob")
    with pytest.raises(HTTPException) as exc_info:
        require_admin(user=user)
    assert exc_info.value.status_code == 403


def test_require_admin_admin_passes(fake_db):
    import lib.db.base as db_base

    db_base.tables["users"].seed(
        {
            "pk": "alice",
            "displayName": "Alice",
            "role": "admin",
            "passwordHash": "x",
            "createdAt": "2026-01-01T00:00:00Z",
        }
    )
    user = AuthUser(sub="alice", role="admin", displayName="Alice")
    result = require_admin(user=user)
    assert result.sub == "alice"


def test_require_admin_rejects_demoted_admin_from_db(fake_db):
    # S-2: token still says admin, but the DB role was changed to readonly →
    # require_admin must re-read and reject.
    import lib.db.base as db_base

    db_base.tables["users"].seed(
        {
            "pk": "alice",
            "displayName": "Alice",
            "role": "readonly",
            "passwordHash": "x",
            "createdAt": "2026-01-01T00:00:00Z",
        }
    )
    user = AuthUser(sub="alice", role="admin", displayName="Alice")
    with pytest.raises(HTTPException) as exc_info:
        require_admin(user=user)
    assert exc_info.value.status_code == 403


def test_sign_and_decode_roundtrip_includes_token_version():
    user = AuthUser(sub="alice", role="admin", displayName="Alice", tokenVersion=3)
    token = sign_token(user)
    decoded = decode_token(token)
    assert decoded.tokenVersion == 3


def test_decode_token_rejects_reset_token():
    # A4: a password-reset token (carries purpose=pwreset) must not be usable as
    # an auth cookie, even though it's signed with the same secret.
    from jose import JWTError

    from lib.auth import sign_reset_token

    reset = sign_reset_token("alice", 0)
    with pytest.raises(JWTError):
        decode_token(reset)


def test_require_auth_rejects_stale_token_version(fake_db):
    import lib.db.base as db_base

    db_base.tables["users"].seed(
        {
            "pk": "alice",
            "displayName": "Alice",
            "role": "admin",
            "passwordHash": "x",
            "createdAt": "2026-01-01T00:00:00Z",
            "tokenVersion": 2,
        }
    )
    stale_token = sign_token(
        AuthUser(sub="alice", role="admin", displayName="Alice", tokenVersion=1)
    )
    with pytest.raises(HTTPException) as exc_info:
        require_auth(token=stale_token)
    assert exc_info.value.status_code == 401


def test_require_auth_accepts_matching_token_version(fake_db):
    import lib.db.base as db_base

    db_base.tables["users"].seed(
        {
            "pk": "alice",
            "displayName": "Alice",
            "role": "admin",
            "passwordHash": "x",
            "createdAt": "2026-01-01T00:00:00Z",
            "tokenVersion": 2,
        }
    )
    token = sign_token(AuthUser(sub="alice", role="admin", displayName="Alice", tokenVersion=2))
    result = require_auth(token=token)
    assert result.sub == "alice"


def test_require_auth_rejects_token_for_deleted_user(fake_db):
    token = sign_token(AuthUser(sub="ghost", role="admin", displayName="Ghost", tokenVersion=0))
    with pytest.raises(HTTPException) as exc_info:
        require_auth(token=token)
    assert exc_info.value.status_code == 401


def test_sign_and_decode_reset_token_roundtrip():
    token = sign_reset_token("alice", token_version=2)
    username, token_version = decode_reset_token(token)
    assert username == "alice"
    assert token_version == 2


def test_decode_reset_token_rejects_login_token():
    from jose import JWTError

    login_token = sign_token(AuthUser(sub="alice", role="admin", displayName="Alice"))
    with pytest.raises(JWTError):
        decode_reset_token(login_token)


def test_decode_reset_token_rejects_expired_token():
    from datetime import datetime, timedelta, timezone

    from jose import JWTError, jwt

    import lib.auth as auth_lib

    expired_payload = {
        "sub": "alice",
        "purpose": "pwreset",
        "tv": 0,
        "exp": int((datetime.now(timezone.utc) - timedelta(minutes=1)).timestamp()),
    }
    expired_token = jwt.encode(expired_payload, auth_lib._jwt_secret, algorithm="HS256")
    with pytest.raises(JWTError):
        decode_reset_token(expired_token)
