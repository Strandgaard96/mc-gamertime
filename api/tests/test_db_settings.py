from lib.db.settings import get_settings, put_settings


def test_get_settings_returns_empty_dict_when_no_row_exists():
    assert get_settings() == {}


def test_put_settings_then_get_settings_roundtrips():
    put_settings({"pk": "instance", "displayName": "My Game Nights"})

    assert get_settings() == {"pk": "instance", "displayName": "My Game Nights"}


def test_put_settings_overwrites_existing_row():
    put_settings({"pk": "instance", "displayName": "First Name"})
    put_settings({"pk": "instance", "displayName": "Second Name"})

    assert get_settings()["displayName"] == "Second Name"
