from robocorp import storage


class TestLibrary:

    def test_list_assets(self):
        asset_list = storage.list_assets()
        print("All assets: ", asset_list)

    def test_get_asset(self):
        name = "Asset 021"
        value = storage.get_asset(name)
        print(f"Asset {name!r}: ", value)

    def test_set_asset(self):
        name = "cosmin"
        provided_value = "cosmin@robocorp.com"
        storage.set_asset(name, provided_value)
        retrieved_value = storage.get_asset(name)
        assert retrieved_value == provided_value
