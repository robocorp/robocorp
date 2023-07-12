0.3.0 (2023-07-12)
-----------------------------

- Removed methods `set_asset`, `get_asset`
- Added new methods for dealing with different asset types:
    - `set_text`, `get_text`
    - `set_json`, `get_json`
    - `set_file`, `get_file`
    - `set_bytes`, `get_bytes`


0.2.0 (2023-06-29)
-----------------------------

- Support for using Asset Storage in VSCode

0.1.2 (2023-06-22)
-----------------------------

- Dependencies update and documentation typo fix.

0.1.1 (2023-06-21)
-----------------------------

- Setting an asset will raise `AssetUploadFailed` in case of failure. 
- Compatibility, typos, logging and documentation fixes.

0.1.0 (2023-06-19)
-----------------------------

- First public release with APIs to:
    - `list_assets`
    - `get_asset`
    - `set_asset`
    - `delete_asset`
