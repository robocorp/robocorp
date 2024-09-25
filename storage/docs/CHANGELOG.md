# Changelog

## Unreleased

## 1.0.5 - 2024-09-25

- Bump requests to 2.32.3

## 1.0.4 - 2024-04-08

- Update package's main README.

## 1.0.3 - 2024-01-14

- Fix main README and update docs.

## 1.0.2 - 2023-11-06

- Fix `list_assets` response parsing.

## 1.0.1 - 2023-10-13

- Fix support for Python 3.8

## 1.0.0 - 2023-09-11

- Change URL path for asset upload

## 0.4.0 - 2023-09-07

- Add support for `RC_DISABLE_SSL`

## 0.3.2 - 2023-07-27

- Fix bug with managing assets containing spaces in their name

## 0.3.1 - 2023-07-18

- Fix INFO logging when uploading the asset (name & content type) 

## 0.3.0 - 2023-07-12

- Removed methods `set_asset`, `get_asset`
- Added new methods for dealing with different asset types:
    - `set_text`, `get_text`
    - `set_json`, `get_json`
    - `set_file`, `get_file`
    - `set_bytes`, `get_bytes`

## 0.2.0 - 2023-06-29

- Support for using Asset Storage in VSCode

## 0.1.2 - 2023-06-22

- Dependencies update and documentation typo fix.

## 0.1.1 - 2023-06-21

- Setting an asset will raise `AssetUploadFailed` in case of failure. 
- Compatibility, typos, logging and documentation fixes.

## 0.1.0 - 2023-06-19

- First public release with APIs to:
    - `list_assets`
    - `get_asset`
    - `set_asset`
    - `delete_asset`
