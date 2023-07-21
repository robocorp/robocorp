<!-- markdownlint-disable -->

# API Overview

## Modules

- [`robocorp.storage`](./robocorp.storage.md#module-robocorpstorage)

## Classes

- [`_client.AssetNotFound`](./robocorp.storage._client.md#class-assetnotfound): No asset with given name/id found.
- [`_client.AssetUploadFailed`](./robocorp.storage._client.md#class-assetuploadfailed): There was an unexpected error while uploading an asset.

## Functions

- [`storage.delete_asset`](./robocorp.storage.md#function-delete_asset): Delete an asset by providing its `name`.
- [`storage.get_bytes`](./robocorp.storage.md#function-get_bytes): Return the given asset as bytes.
- [`storage.get_file`](./robocorp.storage.md#function-get_file): Fetch the given asset and store it in a file.
- [`storage.get_json`](./robocorp.storage.md#function-get_json): Return the given asset as a deserialized JSON object.
- [`storage.get_text`](./robocorp.storage.md#function-get_text): Return the given asset as text.
- [`storage.list_assets`](./robocorp.storage.md#function-list_assets): List all the existing assets.
- [`storage.set_bytes`](./robocorp.storage.md#function-set_bytes): Create or update an asset to contain the given bytes.
- [`storage.set_file`](./robocorp.storage.md#function-set_file): Create or update an asset to contain the contents of the given file.
- [`storage.set_json`](./robocorp.storage.md#function-set_json): Create or update an asset to contain the given object, serialized as JSON.
- [`storage.set_text`](./robocorp.storage.md#function-set_text): Create or update an asset to contain the given string.
