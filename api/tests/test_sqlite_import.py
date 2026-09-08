import importlib.util
import json
import sys
from pathlib import Path

import pytest

from lib.db.sqlite_backend import SqliteTable

EXPORT_PATH = Path(__file__).resolve().parents[2] / "scripts" / "sqlite_export.py"
IMPORT_PATH = Path(__file__).resolve().parents[2] / "scripts" / "sqlite_import.py"


def _load(name, path):
    spec = importlib.util.spec_from_file_location(name, path)
    assert spec is not None
    assert spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    sys.modules[name] = module
    spec.loader.exec_module(module)
    return module


sqlite_export = _load("sqlite_export", EXPORT_PATH)
sqlite_import = _load("sqlite_import", IMPORT_PATH)


def test_import_tables_round_trips_export(tmp_path):
    source_db = str(tmp_path / "source.db")
    SqliteTable(source_db, "games").put_item(Item={"pk": "01GAME", "name": "Wingspan"})
    SqliteTable(source_db, "users").put_item(Item={"pk": "admin", "role": "admin"})
    exported = sqlite_export.export_tables(source_db)

    target_db = str(tmp_path / "target.db")
    sqlite_import.import_tables(target_db, exported)

    target_games = SqliteTable(target_db, "games")
    assert target_games.get_item(Key={"pk": "01GAME"})["Item"]["name"] == "Wingspan"
    target_users = SqliteTable(target_db, "users")
    assert target_users.get_item(Key={"pk": "admin"})["Item"]["role"] == "admin"


def test_import_tables_rejects_unknown_table_without_writing_anything(tmp_path):
    target_db = str(tmp_path / "target.db")
    bad_data = {
        "games": [{"pk": "01GAME", "name": "Wingspan"}],
        "not_a_real_table": [{"pk": "x"}],
    }

    with pytest.raises(ValueError, match="not_a_real_table"):
        sqlite_import.import_tables(target_db, bad_data)

    games = SqliteTable(target_db, "games")
    assert games.scan()["Items"] == []


def test_main_reads_json_files_and_imports(tmp_path):
    in_dir = tmp_path / "in"
    in_dir.mkdir()
    (in_dir / "games.json").write_text(json.dumps([{"pk": "01GAME", "name": "Wingspan"}]))
    target_db = str(tmp_path / "target.db")

    sqlite_import.main(["--db-path", target_db, "--in", str(in_dir)])

    games = SqliteTable(target_db, "games")
    assert games.get_item(Key={"pk": "01GAME"})["Item"]["name"] == "Wingspan"


def test_main_reads_export_tables_naming_with_and_without_dev_suffix(tmp_path):
    in_dir = tmp_path / "in"
    in_dir.mkdir()
    (in_dir / "boardsite-games.json").write_text(json.dumps([{"pk": "01GAME", "name": "Wingspan"}]))
    (in_dir / "boardsite-users-dev.json").write_text(json.dumps([{"pk": "admin", "role": "admin"}]))
    target_db = str(tmp_path / "target.db")

    sqlite_import.main(["--db-path", target_db, "--in", str(in_dir)])

    games = SqliteTable(target_db, "games")
    assert games.get_item(Key={"pk": "01GAME"})["Item"]["name"] == "Wingspan"
    users = SqliteTable(target_db, "users")
    assert users.get_item(Key={"pk": "admin"})["Item"]["role"] == "admin"
