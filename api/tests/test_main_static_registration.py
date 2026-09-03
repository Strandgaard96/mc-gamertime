import importlib


def _route_paths(app) -> list[str]:
    return [route.path for route in app.routes]


def test_storage_router_registered_by_default(monkeypatch):
    # Local-filesystem storage is the default, so the authenticated /storage
    # proxy that serves those files must be there with no configuration.
    monkeypatch.delenv("S3_ENDPOINT_URL", raising=False)
    monkeypatch.delenv("STORAGE_BACKEND", raising=False)
    monkeypatch.delenv("STATIC_DIR", raising=False)
    import main

    importlib.reload(main)
    try:
        assert any(p.startswith("/storage") for p in _route_paths(main.app))
    finally:
        importlib.reload(main)


def test_storage_router_not_registered_on_s3_backend(monkeypatch):
    # Cloud serves objects through CloudFront, so the proxy is dead weight.
    monkeypatch.delenv("S3_ENDPOINT_URL", raising=False)
    monkeypatch.setenv("STORAGE_BACKEND", "s3")
    monkeypatch.delenv("STATIC_DIR", raising=False)
    import main

    importlib.reload(main)
    try:
        assert not any(p.startswith("/storage") for p in _route_paths(main.app))
    finally:
        monkeypatch.delenv("STORAGE_BACKEND", raising=False)
        importlib.reload(main)


def test_storage_router_registered_when_s3_endpoint_set(monkeypatch):
    monkeypatch.setenv("S3_ENDPOINT_URL", "http://seaweedfs:8333")
    monkeypatch.setenv("S3_BUCKET", "boardsite")
    monkeypatch.delenv("STATIC_DIR", raising=False)
    import main

    importlib.reload(main)
    try:
        assert any(p.startswith("/storage") for p in _route_paths(main.app))
    finally:
        monkeypatch.delenv("S3_ENDPOINT_URL", raising=False)
        importlib.reload(main)


def test_storage_router_registered_when_storage_backend_local(monkeypatch):
    monkeypatch.delenv("S3_ENDPOINT_URL", raising=False)
    monkeypatch.setenv("STORAGE_BACKEND", "local")
    monkeypatch.delenv("STATIC_DIR", raising=False)
    import main

    importlib.reload(main)
    try:
        assert any(p.startswith("/storage") for p in _route_paths(main.app))
    finally:
        monkeypatch.delenv("STORAGE_BACKEND", raising=False)
        importlib.reload(main)


def test_spa_fallback_registered_when_static_dir_set(tmp_path, monkeypatch):
    static_dir = tmp_path / "static"
    (static_dir / "assets").mkdir(parents=True)
    (static_dir / "index.html").write_text("<html></html>")

    monkeypatch.setenv("STATIC_DIR", str(static_dir))
    monkeypatch.delenv("S3_ENDPOINT_URL", raising=False)
    import main

    importlib.reload(main)
    try:
        assert "/{path:path}" in _route_paths(main.app)
        assert any(p == "/assets" for p in _route_paths(main.app))
    finally:
        monkeypatch.delenv("STATIC_DIR", raising=False)
        importlib.reload(main)


def test_spa_fallback_not_registered_by_default(monkeypatch):
    monkeypatch.delenv("STATIC_DIR", raising=False)
    monkeypatch.delenv("S3_ENDPOINT_URL", raising=False)
    import main

    importlib.reload(main)
    try:
        assert "/{path:path}" not in _route_paths(main.app)
    finally:
        importlib.reload(main)


def test_spa_fallback_serves_real_files_and_falls_back_to_index(tmp_path, monkeypatch):
    from fastapi.testclient import TestClient

    static_dir = tmp_path / "static"
    (static_dir / "assets").mkdir(parents=True)
    (static_dir / "index.html").write_text("<html>shell</html>")
    (static_dir / "manifest.webmanifest").write_text('{"name": "app"}')

    monkeypatch.setenv("STATIC_DIR", str(static_dir))
    monkeypatch.delenv("S3_ENDPOINT_URL", raising=False)
    import main

    importlib.reload(main)
    try:
        monkeypatch.setattr(main, "_origin_token", "test-origin-token")
        monkeypatch.setattr(main, "_initialized", True)
        c = TestClient(main.app, raise_server_exceptions=False)

        manifest_resp = c.get(
            "/manifest.webmanifest", headers={"x-origin-token": "test-origin-token"}
        )
        assert manifest_resp.text == '{"name": "app"}'

        spa_resp = c.get("/players/alice", headers={"x-origin-token": "test-origin-token"})
        assert spa_resp.text == "<html>shell</html>"
    finally:
        monkeypatch.delenv("STATIC_DIR", raising=False)
        importlib.reload(main)


def test_spa_fallback_rejects_path_traversal(tmp_path, monkeypatch):
    from fastapi.testclient import TestClient

    static_dir = tmp_path / "static"
    (static_dir / "assets").mkdir(parents=True)
    (static_dir / "index.html").write_text("<html>shell</html>")
    secret = tmp_path / "secret.txt"
    secret.write_text("top-secret")

    monkeypatch.setenv("STATIC_DIR", str(static_dir))
    monkeypatch.delenv("S3_ENDPOINT_URL", raising=False)
    import main

    importlib.reload(main)
    try:
        monkeypatch.setattr(main, "_origin_token", "test-origin-token")
        monkeypatch.setattr(main, "_initialized", True)
        c = TestClient(main.app, raise_server_exceptions=False)

        resp = c.get("/../secret.txt", headers={"x-origin-token": "test-origin-token"})
        assert resp.text == "<html>shell</html>"

        resp2 = c.get("/..%2Fsecret.txt", headers={"x-origin-token": "test-origin-token"})
        assert resp2.text == "<html>shell</html>"
    finally:
        monkeypatch.delenv("STATIC_DIR", raising=False)
        importlib.reload(main)
