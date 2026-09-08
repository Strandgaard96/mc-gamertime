from fastapi.testclient import TestClient

from main import app
from tests.conftest import ORIGIN


def test_public_settings_unauthenticated_default():
    c = TestClient(app, raise_server_exceptions=False)
    resp = c.get("/api/settings/public", headers=ORIGIN)
    assert resp.status_code == 200
    assert resp.json() == {"displayName": "MC GamerTime"}


def test_admin_get_settings_readonly_forbidden(authed_client):
    c = authed_client("readonly")
    assert c.get("/api/settings", headers=ORIGIN).status_code == 403


def test_admin_get_settings_default(authed_client):
    c = authed_client("admin")
    resp = c.get("/api/settings", headers=ORIGIN)
    assert resp.status_code == 200
    assert resp.json() == {
        "displayName": "MC GamerTime",
        "bggTokenSet": False,
        "appBaseUrl": None,
        "appBaseUrlEnvFallback": None,
    }


def test_put_settings_display_name_reflected_in_public_and_admin_get(authed_client):
    c = authed_client("admin")
    put_resp = c.put("/api/settings", json={"displayName": "My Game Nights"}, headers=ORIGIN)
    assert put_resp.status_code == 200
    assert put_resp.json()["displayName"] == "My Game Nights"

    assert c.get("/api/settings/public", headers=ORIGIN).json() == {"displayName": "My Game Nights"}
    assert c.get("/api/settings", headers=ORIGIN).json() == {
        "displayName": "My Game Nights",
        "bggTokenSet": False,
        "appBaseUrl": None,
        "appBaseUrlEnvFallback": None,
    }


def test_put_settings_bgg_token_never_returned_in_plaintext(authed_client):
    c = authed_client("admin")
    put_resp = c.put("/api/settings", json={"bggToken": "secret-token-value"}, headers=ORIGIN)
    assert put_resp.status_code == 200
    assert "secret-token-value" not in put_resp.text
    assert put_resp.json()["bggTokenSet"] is True

    get_resp = c.get("/api/settings", headers=ORIGIN)
    assert "secret-token-value" not in get_resp.text
    assert get_resp.json()["bggTokenSet"] is True


def test_put_settings_explicit_null_clears_bgg_token(authed_client):
    c = authed_client("admin")
    c.put("/api/settings", json={"bggToken": "secret-token-value"}, headers=ORIGIN)

    resp = c.put("/api/settings", json={"bggToken": None}, headers=ORIGIN)
    assert resp.status_code == 200
    assert resp.json()["bggTokenSet"] is False


def test_put_settings_display_name_omitted_field_unchanged(authed_client):
    c = authed_client("admin")
    c.put("/api/settings", json={"displayName": "My Game Nights"}, headers=ORIGIN)

    resp = c.put("/api/settings", json={"bggToken": "x"}, headers=ORIGIN)
    assert resp.status_code == 200
    assert resp.json()["displayName"] == "My Game Nights"


def test_put_settings_empty_display_name_422(authed_client):
    c = authed_client("admin")
    resp = c.put("/api/settings", json={"displayName": "   "}, headers=ORIGIN)
    assert resp.status_code == 422


def test_put_settings_display_name_too_long_422(authed_client):
    c = authed_client("admin")
    resp = c.put("/api/settings", json={"displayName": "x" * 61}, headers=ORIGIN)
    assert resp.status_code == 422


def test_put_settings_empty_bgg_token_clears_it(authed_client):
    c = authed_client("admin")
    c.put("/api/settings", json={"bggToken": "secret-token-value"}, headers=ORIGIN)

    resp = c.put("/api/settings", json={"bggToken": "   "}, headers=ORIGIN)
    assert resp.status_code == 200
    assert resp.json()["bggTokenSet"] is False


def test_admin_get_settings_includes_app_base_url_fields(authed_client):
    c = authed_client("admin")
    resp = c.get("/api/settings", headers=ORIGIN)
    assert resp.status_code == 200
    assert resp.json()["appBaseUrl"] is None
    assert resp.json()["appBaseUrlEnvFallback"] is None


def test_admin_get_settings_app_base_url_env_fallback_reflects_env(authed_client, monkeypatch):
    monkeypatch.setenv("APP_BASE_URL", "https://env-fallback.example.com")
    c = authed_client("admin")
    resp = c.get("/api/settings", headers=ORIGIN)
    assert resp.json()["appBaseUrlEnvFallback"] == "https://env-fallback.example.com"


def test_put_settings_app_base_url_stored_and_reflected(authed_client):
    c = authed_client("admin")
    put_resp = c.put(
        "/api/settings", json={"appBaseUrl": "https://games.example.com"}, headers=ORIGIN
    )
    assert put_resp.status_code == 200
    assert put_resp.json()["appBaseUrl"] == "https://games.example.com"

    get_resp = c.get("/api/settings", headers=ORIGIN)
    assert get_resp.json()["appBaseUrl"] == "https://games.example.com"


def test_put_settings_explicit_null_clears_app_base_url(authed_client):
    c = authed_client("admin")
    c.put("/api/settings", json={"appBaseUrl": "https://games.example.com"}, headers=ORIGIN)

    resp = c.put("/api/settings", json={"appBaseUrl": None}, headers=ORIGIN)
    assert resp.status_code == 200
    assert resp.json()["appBaseUrl"] is None


def test_put_settings_app_base_url_rejects_missing_scheme(authed_client):
    c = authed_client("admin")
    resp = c.put("/api/settings", json={"appBaseUrl": "games.example.com"}, headers=ORIGIN)
    assert resp.status_code == 422


def test_put_settings_app_base_url_rejects_scheme_only(authed_client):
    c = authed_client("admin")
    resp = c.put("/api/settings", json={"appBaseUrl": "https://"}, headers=ORIGIN)
    assert resp.status_code == 422


def test_put_settings_empty_app_base_url_clears_it(authed_client):
    c = authed_client("admin")
    c.put("/api/settings", json={"appBaseUrl": "https://games.example.com"}, headers=ORIGIN)

    resp = c.put("/api/settings", json={"appBaseUrl": "   "}, headers=ORIGIN)
    assert resp.status_code == 200
    assert resp.json()["appBaseUrl"] is None
