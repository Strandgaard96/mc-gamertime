from datetime import datetime, timezone

import bcrypt
from fastapi.testclient import TestClient

from lib.auth import sign_reset_token
from main import app
from tests.conftest import ORIGIN, make_auth_cookie

client = TestClient(app, raise_server_exceptions=False)


def _hashed(password: str) -> str:
    return bcrypt.hashpw(password.encode(), bcrypt.gensalt()).decode()


def test_login_success(fake_db):
    fake_db["users"].seed(
        {
            "pk": "admin",
            "displayName": "Magnus",
            "passwordHash": _hashed("TestPass123!"),
            "role": "admin",
            "createdAt": "2026-01-01T00:00:00Z",
        }
    )
    response = client.post(
        "/api/auth/login",
        json={"username": "admin", "password": "TestPass123!"},
        headers=ORIGIN,
    )
    assert response.status_code == 200
    data = response.json()
    assert data["sub"] == "admin"
    assert data["role"] == "admin"
    assert "token" in response.cookies


def test_login_wrong_password(fake_db):
    fake_db["users"].seed(
        {
            "pk": "admin",
            "displayName": "Magnus",
            "passwordHash": _hashed("correct"),
            "role": "admin",
            "createdAt": "2026-01-01T00:00:00Z",
        }
    )
    response = client.post(
        "/api/auth/login",
        json={"username": "admin", "password": "wrong"},
        headers=ORIGIN,
    )
    assert response.status_code == 401


def test_login_unknown_user():
    response = client.post(
        "/api/auth/login",
        json={"username": "nobody", "password": "x"},
        headers=ORIGIN,
    )
    assert response.status_code == 401


def test_me_authenticated():
    c = TestClient(app, raise_server_exceptions=False)
    c.cookies.set("token", make_auth_cookie("admin")["token"])
    response = c.get("/api/auth/me", headers=ORIGIN)
    assert response.status_code == 200
    assert response.json()["sub"] == "testuser"


def test_me_unauthenticated():
    response = client.get("/api/auth/me", headers=ORIGIN)
    assert response.status_code == 401


def test_logout():
    c = TestClient(app, raise_server_exceptions=False)
    c.cookies.set("token", make_auth_cookie("admin")["token"])
    response = c.post("/api/auth/logout", headers=ORIGIN)
    assert response.status_code == 204


def test_logout_invalidates_existing_cookie(fake_db):
    c = TestClient(app, raise_server_exceptions=False)
    cookie = make_auth_cookie("admin")["token"]
    c.cookies.set("token", cookie)

    logout_resp = c.post("/api/auth/logout", headers=ORIGIN)
    assert logout_resp.status_code == 204

    c2 = TestClient(app, raise_server_exceptions=False)
    c2.cookies.set("token", cookie)
    me_resp = c2.get("/api/auth/me", headers=ORIGIN)
    assert me_resp.status_code == 401


def test_logout_cookie_deletion_has_secure_samesite_attributes():
    # Over HTTPS the deletion must mirror how the cookie was set, or the
    # browser keeps it.
    c = TestClient(app, raise_server_exceptions=False, base_url="https://testserver")
    c.cookies.set("token", make_auth_cookie("admin")["token"])
    response = c.post("/api/auth/logout", headers=ORIGIN)
    assert response.status_code == 204
    set_cookie = response.headers.get("set-cookie", "")
    assert "Secure" in set_cookie
    assert "samesite=strict" in set_cookie.lower()


def test_login_cookie_is_secure_over_https(fake_db):
    fake_db["users"].seed(
        {
            "pk": "admin",
            "displayName": "Magnus",
            "passwordHash": _hashed("TestPass123!"),
            "role": "admin",
            "createdAt": "2026-01-01T00:00:00Z",
        }
    )
    c = TestClient(app, raise_server_exceptions=False, base_url="https://testserver")
    response = c.post(
        "/api/auth/login",
        json={"username": "admin", "password": "TestPass123!"},
        headers=ORIGIN,
    )
    assert response.status_code == 200
    assert "Secure" in response.headers.get("set-cookie", "")


def test_login_cookie_omits_secure_over_plain_http(fake_db):
    # A browser refuses to store a Secure cookie delivered over plain HTTP from
    # anything but localhost, so marking it Secure there logs the user straight
    # back out — self-hosting on a LAN address becomes unusable. The cookie has
    # already travelled in the clear at that point, so the flag protects
    # nothing; TLS is what protects it, and then the branch above applies.
    fake_db["users"].seed(
        {
            "pk": "admin",
            "displayName": "Magnus",
            "passwordHash": _hashed("TestPass123!"),
            "role": "admin",
            "createdAt": "2026-01-01T00:00:00Z",
        }
    )
    c = TestClient(app, raise_server_exceptions=False, base_url="http://192.168.1.50")
    response = c.post(
        "/api/auth/login",
        json={"username": "admin", "password": "TestPass123!"},
        headers=ORIGIN,
    )
    assert response.status_code == 200
    set_cookie = response.headers.get("set-cookie", "")
    assert "Secure" not in set_cookie
    # The protections that do not depend on the transport must stay.
    assert "httponly" in set_cookie.lower()
    assert "samesite=strict" in set_cookie.lower()


def test_login_missing_password_returns_422():
    resp = client.post("/api/auth/login", json={"username": "admin"}, headers=ORIGIN)
    assert resp.status_code == 422


def test_login_missing_username_returns_422():
    resp = client.post("/api/auth/login", json={"password": "secret"}, headers=ORIGIN)
    assert resp.status_code == 422


def test_login_escalates_to_429_after_repeated_failures(fake_db, monkeypatch):
    import routes.auth as auth_routes

    monkeypatch.setattr(auth_routes.time, "sleep", lambda _: None)
    fake_db["users"].seed(
        {
            "pk": "admin",
            "displayName": "Magnus",
            "passwordHash": _hashed("correct"),
            "role": "admin",
            "createdAt": "2026-01-01T00:00:00Z",
        }
    )

    for _ in range(4):
        resp = client.post(
            "/api/auth/login", json={"username": "admin", "password": "wrong"}, headers=ORIGIN
        )
        assert resp.status_code == 401

    resp = client.post(
        "/api/auth/login", json={"username": "admin", "password": "wrong"}, headers=ORIGIN
    )
    assert resp.status_code == 429
    assert "Retry-After" in resp.headers


def test_login_success_resets_failed_attempts(fake_db, monkeypatch):
    import routes.auth as auth_routes

    monkeypatch.setattr(auth_routes.time, "sleep", lambda _: None)
    fake_db["users"].seed(
        {
            "pk": "admin",
            "displayName": "Magnus",
            "passwordHash": _hashed("correct"),
            "role": "admin",
            "createdAt": "2026-01-01T00:00:00Z",
            "failedAttempts": 2,
            "lastFailureAt": "2026-01-01T00:00:00+00:00",
        }
    )

    resp = client.post(
        "/api/auth/login", json={"username": "admin", "password": "correct"}, headers=ORIGIN
    )
    assert resp.status_code == 200
    assert fake_db["users"].get_item(Key={"pk": "admin"})["Item"]["failedAttempts"] == 0


def test_login_old_failures_decay_after_reset_window(fake_db, monkeypatch):
    import routes.auth as auth_routes

    monkeypatch.setattr(auth_routes.time, "sleep", lambda _: None)
    fake_db["users"].seed(
        {
            "pk": "admin",
            "displayName": "Magnus",
            "passwordHash": _hashed("correct"),
            "role": "admin",
            "createdAt": "2026-01-01T00:00:00Z",
            "failedAttempts": 5,
            "lastFailureAt": "2020-01-01T00:00:00+00:00",
        }
    )

    resp = client.post(
        "/api/auth/login", json={"username": "admin", "password": "wrong"}, headers=ORIGIN
    )
    assert resp.status_code == 401


def test_failed_login_uses_atomic_increment(fake_db, monkeypatch):
    import routes.auth as auth_routes

    monkeypatch.setattr(auth_routes.time, "sleep", lambda _: None)
    fake_db["users"].seed(
        {
            "pk": "alice",
            "displayName": "Alice",
            "role": "readonly",
            "passwordHash": _hashed("right"),
            "createdAt": "2026-01-01T00:00:00Z",
        }
    )
    resp = client.post(
        "/api/auth/login", json={"username": "alice", "password": "wrong"}, headers=ORIGIN
    )
    assert resp.status_code == 401
    stored = fake_db["users"].get_item(Key={"pk": "alice"})["Item"]
    assert stored["failedAttempts"] == 1
    assert stored["lastFailureAt"]
    # The full user item must NOT have been rewritten by put_user (atomic update only):
    assert stored["displayName"] == "Alice"


def test_login_rate_limit_429_on_sixth_attempt(fake_db):
    fake_db["users"].seed(
        {
            "pk": "ratelimituser",
            "displayName": "Test",
            "passwordHash": _hashed("correct"),
            "role": "readonly",
            "createdAt": "2026-01-01T00:00:00Z",
        }
    )
    for _ in range(5):
        client.post(
            "/api/auth/login",
            json={"username": "ratelimituser", "password": "wrong"},
            headers=ORIGIN,
        )
    resp = client.post(
        "/api/auth/login",
        json={"username": "ratelimituser", "password": "wrong"},
        headers=ORIGIN,
    )
    assert resp.status_code == 429
    assert "retry-after" in resp.headers


def test_failed_login_does_not_put_full_item(fake_db, monkeypatch):
    import routes.auth as auth_routes

    monkeypatch.setattr(auth_routes.time, "sleep", lambda _: None)
    fake_db["users"].seed(
        {
            "pk": "alice",
            "displayName": "Alice",
            "role": "readonly",
            "passwordHash": _hashed("right"),
            "createdAt": "2026-01-01T00:00:00Z",
        }
    )
    calls = []
    monkeypatch.setattr(auth_routes, "put_user", lambda item: calls.append(item))
    resp = client.post(
        "/api/auth/login", json={"username": "alice", "password": "wrong"}, headers=ORIGIN
    )
    assert resp.status_code == 401
    assert calls == []  # failure path must use the atomic update, not put_user


def test_forgot_password_sends_email_when_user_has_email(fake_db, mocker, monkeypatch):
    # F-6: with no appBaseUrl/APP_BASE_URL, the cloud path refuses to build a
    # link from the spoofable Host header. Set APP_BASE_URL so a link can be built.
    monkeypatch.setenv("APP_BASE_URL", "https://games.example.com")
    fake_db["users"].seed(
        {
            "pk": "alice",
            "displayName": "Alice",
            "passwordHash": _hashed("old-pass"),
            "role": "readonly",
            "email": "alice@example.com",
            "createdAt": "2026-01-01T00:00:00Z",
            "tokenVersion": 0,
        }
    )
    send_email = mocker.patch("routes.auth.send_email")
    response = client.post("/api/auth/forgot-password", json={"username": "alice"}, headers=ORIGIN)
    assert response.status_code == 204
    send_email.assert_called_once()
    assert send_email.call_args.kwargs["to"] == "alice@example.com"


def test_forgot_password_no_base_url_on_cloud_does_not_send(fake_db, mocker, monkeypatch):
    # F-6: cloud (SECRETS_PROVIDER!=env) with no appBaseUrl/APP_BASE_URL must not
    # email a Host-header-derived (poisonable) link. Still returns 204 (no oracle).
    monkeypatch.delenv("APP_BASE_URL", raising=False)
    monkeypatch.setenv("SECRETS_PROVIDER", "ssm")
    fake_db["users"].seed(
        {
            "pk": "alice",
            "displayName": "Alice",
            "passwordHash": _hashed("old-pass"),
            "role": "readonly",
            "email": "alice@example.com",
            "createdAt": "2026-01-01T00:00:00Z",
            "tokenVersion": 0,
        }
    )
    send_email = mocker.patch("routes.auth.send_email")
    response = client.post("/api/auth/forgot-password", json={"username": "alice"}, headers=ORIGIN)
    assert response.status_code == 204
    send_email.assert_not_called()


def test_forgot_password_ignores_forged_host_header_when_app_base_url_set(
    fake_db, mocker, monkeypatch
):
    monkeypatch.setenv("APP_BASE_URL", "https://games.example.com")
    fake_db["users"].seed(
        {
            "pk": "alice",
            "displayName": "Alice",
            "passwordHash": _hashed("old-pass"),
            "role": "readonly",
            "email": "alice@example.com",
            "createdAt": "2026-01-01T00:00:00Z",
            "tokenVersion": 0,
        }
    )
    send_email = mocker.patch("routes.auth.send_email")
    response = client.post(
        "/api/auth/forgot-password",
        json={"username": "alice"},
        headers={**ORIGIN, "Host": "evil.example.com"},
    )
    assert response.status_code == 204
    body = send_email.call_args.kwargs["body"]
    assert "https://games.example.com/reset-password?token=" in body
    assert "evil.example.com" not in body


def test_forgot_password_db_app_base_url_wins_over_env(fake_db, mocker, monkeypatch):
    monkeypatch.setenv("APP_BASE_URL", "https://env-value.example.com")
    fake_db["settings"].seed({"pk": "instance", "appBaseUrl": "https://db-value.example.com"})
    fake_db["users"].seed(
        {
            "pk": "alice",
            "displayName": "Alice",
            "passwordHash": _hashed("old-pass"),
            "role": "readonly",
            "email": "alice@example.com",
            "createdAt": "2026-01-01T00:00:00Z",
            "tokenVersion": 0,
        }
    )
    send_email = mocker.patch("routes.auth.send_email")
    response = client.post("/api/auth/forgot-password", json={"username": "alice"}, headers=ORIGIN)
    assert response.status_code == 204
    body = send_email.call_args.kwargs["body"]
    assert "https://db-value.example.com/reset-password?token=" in body


def test_forgot_password_no_email_on_file_no_send(fake_db, mocker):
    fake_db["users"].seed(
        {
            "pk": "bob",
            "displayName": "Bob",
            "passwordHash": _hashed("old-pass"),
            "role": "readonly",
            "createdAt": "2026-01-01T00:00:00Z",
            "tokenVersion": 0,
        }
    )
    send_email = mocker.patch("routes.auth.send_email")
    response = client.post("/api/auth/forgot-password", json={"username": "bob"}, headers=ORIGIN)
    assert response.status_code == 204
    send_email.assert_not_called()


def test_forgot_password_unknown_user_same_response(mocker):
    send_email = mocker.patch("routes.auth.send_email")
    response = client.post("/api/auth/forgot-password", json={"username": "nobody"}, headers=ORIGIN)
    assert response.status_code == 204
    send_email.assert_not_called()


def test_reset_password_success_then_login_with_new_password(fake_db):
    fake_db["users"].seed(
        {
            "pk": "alice",
            "displayName": "Alice",
            "passwordHash": _hashed("old-pass"),
            "role": "readonly",
            "createdAt": "2026-01-01T00:00:00Z",
            "tokenVersion": 0,
        }
    )
    token = sign_reset_token("alice", token_version=0)
    response = client.post(
        "/api/auth/reset-password",
        json={"token": token, "newPassword": "new-pass-123"},
        headers=ORIGIN,
    )
    assert response.status_code == 204

    login_response = client.post(
        "/api/auth/login",
        json={"username": "alice", "password": "new-pass-123"},
        headers=ORIGIN,
    )
    assert login_response.status_code == 200


def test_reset_password_token_rejected_after_use(fake_db):
    fake_db["users"].seed(
        {
            "pk": "alice",
            "displayName": "Alice",
            "passwordHash": _hashed("old-pass"),
            "role": "readonly",
            "createdAt": "2026-01-01T00:00:00Z",
            "tokenVersion": 0,
        }
    )
    token = sign_reset_token("alice", token_version=0)
    first = client.post(
        "/api/auth/reset-password",
        json={"token": token, "newPassword": "new-pass-123"},
        headers=ORIGIN,
    )
    assert first.status_code == 204

    replay = client.post(
        "/api/auth/reset-password",
        json={"token": token, "newPassword": "another-pass"},
        headers=ORIGIN,
    )
    assert replay.status_code == 400


def test_reset_password_short_new_password_returns_422(fake_db):
    fake_db["users"].seed(
        {
            "pk": "alice",
            "displayName": "Alice",
            "passwordHash": _hashed("old-pass"),
            "role": "readonly",
            "createdAt": "2026-01-01T00:00:00Z",
            "tokenVersion": 0,
        }
    )
    token = sign_reset_token("alice", token_version=0)
    response = client.post(
        "/api/auth/reset-password",
        json={"token": token, "newPassword": "short1"},
        headers=ORIGIN,
    )
    assert response.status_code == 422


def test_reset_password_eleven_char_password_returns_422(fake_db):
    fake_db["users"].seed(
        {
            "pk": "alice",
            "displayName": "Alice",
            "passwordHash": _hashed("old-pass-long"),
            "role": "readonly",
            "createdAt": "2026-01-01T00:00:00Z",
            "tokenVersion": 0,
        }
    )
    token = sign_reset_token("alice", token_version=0)
    response = client.post(
        "/api/auth/reset-password",
        json={"token": token, "newPassword": "a" * 11},
        headers=ORIGIN,
    )
    assert response.status_code == 422


def test_reset_password_password_too_long_returns_422(fake_db):
    fake_db["users"].seed(
        {
            "pk": "alice",
            "displayName": "Alice",
            "passwordHash": _hashed("old-pass-long"),
            "role": "readonly",
            "createdAt": "2026-01-01T00:00:00Z",
            "tokenVersion": 0,
        }
    )
    token = sign_reset_token("alice", token_version=0)
    response = client.post(
        "/api/auth/reset-password",
        json={"token": token, "newPassword": "a" * 1025},
        headers=ORIGIN,
    )
    assert response.status_code == 422


def test_reset_password_invalid_token_400():
    response = client.post(
        "/api/auth/reset-password",
        json={"token": "not.a.valid.token", "newPassword": "new-pass-123"},
        headers=ORIGIN,
    )
    assert response.status_code == 400


def test_reset_password_rate_limit_429_on_sixth_attempt():
    for _ in range(5):
        client.post(
            "/api/auth/reset-password",
            json={"token": "not.a.valid.token", "newPassword": "new-pass-123"},
            headers=ORIGIN,
        )
    resp = client.post(
        "/api/auth/reset-password",
        json={"token": "not.a.valid.token", "newPassword": "new-pass-123"},
        headers=ORIGIN,
    )
    assert resp.status_code == 429
    assert "retry-after" in resp.headers


# bcrypt raises ValueError above 72 bytes rather than truncating, so anything
# that reaches hashpw/checkpw with a longer password 500s. The login path is
# unauthenticated, and 72 *bytes* is only 36 accented characters, so an ordinary
# non-ASCII passphrase can trip it.
_OVER_72_BYTES_ASCII = "a" * 100
_OVER_72_BYTES_ACCENTED = "é" * 40  # 40 chars, 80 bytes


def test_login_over_72_byte_password_is_rejected_not_500(fake_db):
    fake_db["users"].seed(
        {
            "pk": "admin",
            "displayName": "Magnus",
            "passwordHash": _hashed("correct-horse-battery"),
            "role": "admin",
            "createdAt": "2026-01-01T00:00:00Z",
        }
    )
    response = client.post(
        "/api/auth/login",
        json={"username": "admin", "password": _OVER_72_BYTES_ASCII},
        headers=ORIGIN,
    )
    assert response.status_code == 401


def test_login_multibyte_password_over_72_bytes_is_rejected_not_500(fake_db):
    fake_db["users"].seed(
        {
            "pk": "admin",
            "displayName": "Magnus",
            "passwordHash": _hashed("correct-horse-battery"),
            "role": "admin",
            "createdAt": "2026-01-01T00:00:00Z",
        }
    )
    response = client.post(
        "/api/auth/login",
        json={"username": "admin", "password": _OVER_72_BYTES_ACCENTED},
        headers=ORIGIN,
    )
    assert response.status_code == 401


def test_reset_password_over_72_bytes_is_422(fake_db):
    fake_db["users"].seed(
        {
            "pk": "alice",
            "displayName": "Alice",
            "email": "alice@example.com",
            "passwordHash": _hashed("old-password-here"),
            "role": "readonly",
            "tokenVersion": 0,
            "createdAt": "2026-01-01T00:00:00Z",
        }
    )
    token = sign_reset_token("alice", token_version=0)
    response = client.post(
        "/api/auth/reset-password",
        json={"token": token, "newPassword": _OVER_72_BYTES_ASCII},
        headers=ORIGIN,
    )
    assert response.status_code == 422


def test_login_unknown_user_with_over_72_byte_password_is_401_not_500(fake_db):
    # The unknown-user branch runs a dummy bcrypt call to equalise timing, which
    # is a second place an over-long password reaches bcrypt. Regression: this
    # 500'd in production, where the seeded-user tests above could not catch it.
    response = client.post(
        "/api/auth/login",
        json={"username": "nobody-at-all", "password": _OVER_72_BYTES_ASCII},
        headers=ORIGIN,
    )
    assert response.status_code == 401


def test_login_with_decimal_failed_attempts_from_dynamodb(fake_db):
    # DynamoDB returns every number as decimal.Decimal. The lockout backoff fed
    # that straight into timedelta(seconds=...), which rejects Decimal, so any
    # account with a recent failed attempt 500'd on every subsequent login —
    # including with the correct password. SQLite returns ints, so this only
    # ever showed on the cloud deployment.
    from decimal import Decimal

    fake_db["users"].seed(
        {
            "pk": "admin",
            "displayName": "Magnus",
            "passwordHash": _hashed("TestPass123!"),
            "role": "admin",
            "failedAttempts": Decimal("1"),
            "lastFailureAt": datetime.now(timezone.utc).isoformat(),
            "createdAt": "2026-01-01T00:00:00Z",
        }
    )
    response = client.post(
        "/api/auth/login",
        json={"username": "admin", "password": "TestPass123!"},
        headers=ORIGIN,
    )
    assert response.status_code == 200
