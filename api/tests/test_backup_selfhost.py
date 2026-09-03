import subprocess
import tarfile
from pathlib import Path

SCRIPT = Path(__file__).resolve().parents[2] / "scripts" / "backup-selfhost.sh"


def _run(repo_root, *args):
    return subprocess.run(
        ["sh", str(SCRIPT), *args],
        cwd=repo_root,
        capture_output=True,
        text=True,
        check=True,
    )


def _make_repo_root(tmp_path):
    (tmp_path / "config" / "app").mkdir(parents=True)
    (tmp_path / "config" / "app" / "boardsite.db").write_text("fake db contents")
    return tmp_path


def test_creates_archive_containing_config_app(tmp_path):
    repo_root = _make_repo_root(tmp_path)
    _run(repo_root, "--dest", "backups")
    archives = list((repo_root / "backups").glob("boardsite-backup-*.tar.gz"))
    assert len(archives) == 1

    with tarfile.open(archives[0], "r:gz") as tar:
        names = tar.getnames()
    assert any(name.endswith("config/app/boardsite.db") for name in names)


def test_fails_without_config_app_dir(tmp_path):
    result = subprocess.run(
        ["sh", str(SCRIPT)],
        cwd=tmp_path,
        capture_output=True,
        text=True,
    )
    assert result.returncode != 0
    assert "config/app not found" in result.stderr


def test_keep_prunes_oldest_archives_beyond_limit(tmp_path):
    repo_root = _make_repo_root(tmp_path)
    dest = repo_root / "backups"
    dest.mkdir()
    # Pre-seed 3 fake older archives with sortable timestamps.
    for stamp in ("20260101T000000", "20260102T000000", "20260103T000000"):
        (dest / f"boardsite-backup-{stamp}.tar.gz").write_text("old")

    _run(repo_root, "--dest", "backups", "--keep", "2")

    remaining = sorted(p.name for p in dest.glob("boardsite-backup-*.tar.gz"))
    # 3 pre-seeded + 1 new = 4 total, --keep 2 prunes the 2 oldest pre-seeded ones.
    assert len(remaining) == 2
    assert "20260101T000000" not in remaining[0]
    assert "20260102T000000" not in "".join(remaining)
