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
        asset = storage._create_asset(name)
        yield asset
        try:
            storage.delete_asset(name)
        except storage.AssetNotFound:
            pass

    def test_list_assets(self, ensured_asset):
        assets = storage.list_assets()
        asset_names = [asset["name"] for asset in assets]
        assert ensured_asset["name"] in asset_names

    def test_get_asset(self, ensured_asset):
        value = storage.get_asset(ensured_asset["name"])
        assert value == ""

    def test_delete_asset(self, ensured_asset):
        name = ensured_asset["name"]
        storage.delete_asset(name)
        with pytest.raises(storage.AssetNotFound):
            storage.delete_asset(name)

    def test_set_asset(self):
        name = "cosmin"
        provided_value = "cosmin@robocorp.com"
        storage.set_asset(name, provided_value)
        retrieved_value = storage.get_asset(name)
        assert retrieved_value == provided_value

        # Setting also replaces already existing assets with newer values.
        extra = " is my e-mail"
        storage.set_asset(name, provided_value + extra)
        retrieved_value = storage.get_asset(name)
        assert retrieved_value == provided_value + extra
