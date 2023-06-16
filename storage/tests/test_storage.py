from robocorp import storage


class TestLibrary:

    def test_list_assets(self):
        asset_list = storage.list_assets()
        print(asset_list)
