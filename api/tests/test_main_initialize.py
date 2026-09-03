import pytest


def _seed_existing_user():
    import lib.db.base as db_base

    db_base.tables["users"].seed(
        {
            "pk": "existing",
            "username": "existing",
            "displayName": "Existing",
            "role": "admin",
            "passwordHash": "hash",
        }
    )


def test_initialize_env_provider_reads_env_vars(monkeypatch):
    import main

    monkeypatch.setattr(main, "_initialized", False)
    monkeypatch.setattr(main, "SECRETS_PROVIDER", "env")
    monkeypatch.setenv("JWT_SECRET", "supersecretvalue")
    monkeypatch.setenv("ORIGIN_TOKEN", "sometoken")
    monkeypatch.setenv("BGG_TOKEN", "")
    _seed_existing_user()

    main._initialize()

    assert main._initialized is True
    assert main._origin_token == "sometoken"


def test_initialize_env_provider_empty_origin_token_allowed_when_guard_disabled(monkeypatch):
    import main

    monkeypatch.setattr(main, "_initialized", False)
    monkeypatch.setattr(main, "SECRETS_PROVIDER", "env")
    monkeypatch.setenv("JWT_SECRET", "supersecretvalue")
    monkeypatch.setenv("ORIGIN_TOKEN", "")
    monkeypatch.setenv("BGG_TOKEN", "")
    monkeypatch.setenv("ORIGIN_GUARD_ENABLED", "false")
    _seed_existing_user()

    main._initialize()

    assert main._initialized is True
    assert main._origin_token == ""


def test_initialize_env_provider_empty_origin_token_raises_when_guard_enabled(monkeypatch):
    import main

    monkeypatch.setattr(main, "_initialized", False)
    monkeypatch.setattr(main, "SECRETS_PROVIDER", "env")
    monkeypatch.setenv("JWT_SECRET", "supersecretvalue")
    monkeypatch.setenv("ORIGIN_TOKEN", "")
    monkeypatch.setenv("BGG_TOKEN", "")
    monkeypatch.delenv("ORIGIN_GUARD_ENABLED", raising=False)
    monkeypatch.delenv("DEV_MODE", raising=False)

    with pytest.raises(RuntimeError):
        main._initialize()


def test_initialize_env_provider_missing_jwt_secret_raises(monkeypatch):
    import main

    monkeypatch.setattr(main, "_initialized", False)
    monkeypatch.setattr(main, "SECRETS_PROVIDER", "env")
    monkeypatch.delenv("JWT_SECRET", raising=False)

    with pytest.raises(RuntimeError):
        main._initialize()


def test_initialize_env_provider_change_me_jwt_secret_raises(monkeypatch):
    import main

    monkeypatch.setattr(main, "_initialized", False)
    monkeypatch.setattr(main, "SECRETS_PROVIDER", "env")
    monkeypatch.setenv("JWT_SECRET", "CHANGE_ME")

    with pytest.raises(RuntimeError):
        main._initialize()


def test_bootstrap_admin_skips_when_unset_and_users_exist(monkeypatch):
    import main

    monkeypatch.delenv("ADMIN_USERNAME", raising=False)
    monkeypatch.delenv("ADMIN_PASSWORD", raising=False)
    _seed_existing_user()

    main._bootstrap_admin_user()

    from lib.db.users import get_user

    assert get_user("admin") is None


def test_bootstrap_admin_raises_when_unset_and_no_users(monkeypatch):
    import main

    monkeypatch.delenv("ADMIN_USERNAME", raising=False)
    monkeypatch.delenv("ADMIN_PASSWORD", raising=False)

    with pytest.raises(RuntimeError, match="No users found"):
        main._bootstrap_admin_user()


def test_bootstrap_admin_creates_user_when_new(monkeypatch):
    import bcrypt

    import main

    monkeypatch.setenv("ADMIN_USERNAME", "admin")
    monkeypatch.setenv("ADMIN_PASSWORD", "supersecret")

    main._bootstrap_admin_user()

    from lib.db.users import get_user

    user = get_user("admin")
    assert user is not None
    assert user["role"] == "admin"
    assert user["displayName"] == "admin"
    assert bcrypt.checkpw(b"supersecret", user["passwordHash"].encode())


def test_bootstrap_admin_does_not_overwrite_existing_user(monkeypatch):
    import lib.db.base as db_base
    import main

    db_base.tables["users"].seed(
        {
            "pk": "admin",
            "username": "admin",
            "displayName": "Custom Name",
            "role": "readonly",
            "passwordHash": "untouched-hash",
        }
    )
    monkeypatch.setenv("ADMIN_USERNAME", "admin")
    monkeypatch.setenv("ADMIN_PASSWORD", "supersecret")

    main._bootstrap_admin_user()

    from lib.db.users import get_user

    user = get_user("admin")
    assert user["role"] == "readonly"
    assert user["displayName"] == "Custom Name"
    assert user["passwordHash"] == "untouched-hash"


def test_bootstrap_admin_partial_config_raises(monkeypatch):
    import main

    monkeypatch.setenv("ADMIN_USERNAME", "admin")
    monkeypatch.delenv("ADMIN_PASSWORD", raising=False)

    with pytest.raises(RuntimeError):
        main._bootstrap_admin_user()
