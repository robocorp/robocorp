import random
import string

import pytest

from robocorp import storage

random_str = lambda length: "".join(  # noqa: E731
    random.choice(string.ascii_lowercase) for _ in range(length)
)


@pytest.mark.xfail(reason="not ready for CI yet (Control Room injected env vars)")
class TestLibrary:
    """Tests the library directly by calling its public interface."""

    @staticmethod
    @pytest.fixture(scope="class")
    def ensured_asset():
        """Creates an asset with a random name with a lifespan of the test case."""
        name = f"cosmin-{random_str(8)}"
        storage.set_text(name, random_str(16), wait=True)
        yield name
        try:
            storage.delete_asset(name)
        except storage.AssetNotFound:
            pass

    @staticmethod
    @pytest.fixture(scope="class")
    def cleanup_assets():
        yield
        assets = storage.list_assets()
        for asset in assets:
            if asset.startswith("cosmin-"):
                storage.delete_asset(asset)

    def test_list_assets(self, ensured_asset):
        assets = storage.list_assets()
        assert ensured_asset in assets

    def test_delete_asset(self, ensured_asset):
        storage.delete_asset(ensured_asset)
        with pytest.raises(storage.AssetNotFound):
            storage.delete_asset(ensured_asset)

    def test_text_asset(self, cleanup_assets):
        name = "cosmin-text"
        text = "cosmin@robocorp.com"
        storage.set_text(name, text)
        obtained_text = storage.get_text(name)
        assert obtained_text == text

    def test_bytes_asset(self, cleanup_assets):
        name = "cosmin-bytes space"
        data = b"cosmin@robocorp.com"
        storage.set_bytes(name, data)
        obtained_data = storage.get_bytes(name)
        assert obtained_data == data

    def test_json_asset(self, cleanup_assets):
        name = "cosmin-json"
        value = {"email": "cosmin@robocorp.com"}
        storage.set_json(name, value)
        obtained_value = storage.get_json(name)
        assert obtained_value == value

    def test_file_asset(self, cleanup_assets, tmp_path):
        path = tmp_path / "cosmin.txt"
        content = "cosmin@robocorp.com"
        path.write_text(content)
        name = "cosmin-file"
        storage.set_file(name, path)
        obtained_path = tmp_path / "obtained_cosmin.txt"
        obtained_path = storage.get_file(name, obtained_path)
        assert obtained_path.read_text() == content
