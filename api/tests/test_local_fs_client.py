import pytest

from lib.storage import LocalFsClient


@pytest.fixture
def client(tmp_path):
    return LocalFsClient(str(tmp_path))


def test_put_then_get_round_trips_bytes_and_content_type(client):
    client.put_object(Bucket="x", Key="avatars/alice.png", Body=b"\x89PNG", ContentType="image/png")
    obj = client.get_object(Bucket="x", Key="avatars/alice.png")
    assert b"".join(obj["Body"].iter_chunks()) == b"\x89PNG"
    assert obj["ContentType"] == "image/png"


def test_get_missing_key_raises_file_not_found(client):
    with pytest.raises(FileNotFoundError):
        client.get_object(Bucket="x", Key="avatars/missing.png")


def test_put_creates_parent_directories(client, tmp_path):
    client.put_object(
        Bucket="x", Key="blog-images/01ABC.png", Body=b"data", ContentType="image/png"
    )
    assert (tmp_path / "blog-images" / "01ABC.png").is_file()


def test_delete_removes_object_and_metadata(client, tmp_path):
    client.put_object(Bucket="x", Key="avatars/alice.png", Body=b"data", ContentType="image/png")
    client.delete_object(Bucket="x", Key="avatars/alice.png")
    with pytest.raises(FileNotFoundError):
        client.get_object(Bucket="x", Key="avatars/alice.png")
    assert not (tmp_path / "avatars" / "alice.png").exists()
    assert not (tmp_path / "avatars" / "alice.png.meta").exists()


def test_delete_missing_object_does_not_raise(client):
    client.delete_object(Bucket="x", Key="avatars/never-existed.png")


def test_put_object_rejects_path_traversal_key(client, tmp_path):
    with pytest.raises(ValueError):
        client.put_object(Bucket="x", Key="../../etc/passwd", Body=b"data", ContentType="image/png")
    assert not (tmp_path.parent.parent / "etc" / "passwd").exists()


def test_get_object_rejects_path_traversal_key(client):
    with pytest.raises(ValueError):
        client.get_object(Bucket="x", Key="../../etc/passwd")


def test_delete_object_rejects_path_traversal_key(client):
    with pytest.raises(ValueError):
        client.delete_object(Bucket="x", Key="../../etc/passwd")


def test_put_object_rejects_absolute_path_key(client):
    with pytest.raises(ValueError):
        client.put_object(Bucket="x", Key="/etc/passwd", Body=b"data", ContentType="image/png")


def test_put_then_get_still_works_for_valid_key_after_validation(client):
    client.put_object(Bucket="x", Key="avatars/alice.png", Body=b"\x89PNG", ContentType="image/png")
    obj = client.get_object(Bucket="x", Key="avatars/alice.png")
    assert b"".join(obj["Body"].iter_chunks()) == b"\x89PNG"
    assert obj["ContentType"] == "image/png"
