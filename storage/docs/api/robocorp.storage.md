<!-- markdownlint-disable -->

# module `robocorp.storage`

# Functions

______________________________________________________________________

## `list_assets`

List all the existing assets.

**Returns:**
A list of available assets' names

[**Link to source**](https://github.com/robocorp/robocorp/tree/master/storage/src/robocorp/storage/__init__.py#L45)

```python
list_assets() → List[str]
```

______________________________________________________________________

## `delete_asset`

Delete an asset by providing its `name`.

This operation cannot be undone.

**Args:**

- <b>`name`</b>:  Asset to delete

**Raises:**

- <b>`AssetNotFound`</b>:  Asset with the given name does not exist

[**Link to source**](https://github.com/robocorp/robocorp/tree/master/storage/src/robocorp/storage/__init__.py#L74)

```python
delete_asset(name: str)
```

______________________________________________________________________

## `get_text`

Return the given asset as text.

**Arguments:**

- <b>`name`</b>:  Name of asset

**Returns:**
Asset content as text

**Raises:**

- <b>`AssetNotFound`</b>:  No asset defined with given name

[**Link to source**](https://github.com/robocorp/robocorp/tree/master/storage/src/robocorp/storage/__init__.py#L114)

```python
get_text(name: str) → str
```

______________________________________________________________________

## `get_json`

Return the given asset as a deserialized JSON object.

**Arguments:**

- <b>`name`</b>:  Name of asset
- <b>`**kwargs`</b>:  Additional parameters for `json.loads`

**Returns:**
Asset content as a Python object (dict, list etc.)

**Raises:**

- <b>`AssetNotFound`</b>:  No asset defined with given name
- <b>`JSONDecodeError`</b>:  Asset was not valid JSON

[**Link to source**](https://github.com/robocorp/robocorp/tree/master/storage/src/robocorp/storage/__init__.py#L130)

```python
get_json(
    name: str,
    **kwargs
) → Union[Dict[str, ForwardRef('JSON')], List[ForwardRef('JSON')], str, int, float, bool, NoneType]
```

______________________________________________________________________

## `get_file`

Fetch the given asset and store it in a file.

**Arguments:**

- <b>`name`</b>:  Name of asset
- <b>`path`</b>:  Destination path for downloaded file
- <b>`exist_ok`</b>:  Overwrite file if it already exists

**Returns:**
Path to created file

**Raises:**

- <b>`AssetNotFound`</b>:  No asset defined with given name
- <b>`FileExistsError`</b>:  Destination already exists

[**Link to source**](https://github.com/robocorp/robocorp/tree/master/storage/src/robocorp/storage/__init__.py#L148)

```python
get_file(name: str, path: Union[PathLike, str], exist_ok=False) → Path
```

______________________________________________________________________

## `get_bytes`

Return the given asset as bytes.

**Arguments:**

- <b>`name`</b>:  Name of asset

**Returns:**
Asset content as bytes

**Raises:**

- <b>`AssetNotFound`</b>:  No asset defined with given name

[**Link to source**](https://github.com/robocorp/robocorp/tree/master/storage/src/robocorp/storage/__init__.py#L173)

```python
get_bytes(name: str) → bytes
```

______________________________________________________________________

## `set_text`

Create or update an asset to contain the given string.

**Arguments:**

- <b>`name`</b>:  Name of asset
- <b>`text`</b>:  Text content for asset
- <b>`wait`</b>:  Wait for asset to update

[**Link to source**](https://github.com/robocorp/robocorp/tree/master/storage/src/robocorp/storage/__init__.py#L204)

```python
set_text(name: str, text: str, wait: bool = True)
```

______________________________________________________________________

## `set_json`

Create or update an asset to contain the given object, serialized as JSON.

**Arguments:**

- <b>`name`</b>:  Name of asset
- <b>`value`</b>:  Value for asset, e.g. dict or list
- <b>`wait`</b>:  Wait for asset to update
- <b>`**kwargs`</b>:  Additional arguments for `json.dumps`

[**Link to source**](https://github.com/robocorp/robocorp/tree/master/storage/src/robocorp/storage/__init__.py#L217)

```python
set_json(
    name: str,
    value: Optional[Dict[str, ForwardRef('JSON')], List[ForwardRef('JSON')], str, int, float, bool],
    wait: bool = True,
    **kwargs
)
```

______________________________________________________________________

## `set_file`

Create or update an asset to contain the contents of the given file.

**Arguments:**

- <b>`name`</b>:  Name of asset
- <b>`path`</b>:  Path to file
- <b>`content_type`</b>:  Content type (or mimetype) of file, detected automatically from file extension if not defined
- <b>`wait`</b>:  Wait for asset to update

[**Link to source**](https://github.com/robocorp/robocorp/tree/master/storage/src/robocorp/storage/__init__.py#L231)

```python
set_file(
    name: str,
    path: Union[PathLike, str],
    content_type: Optional[str] = None,
    wait: bool = True
)
```

______________________________________________________________________

## `set_bytes`

Create or update an asset to contain the given bytes.

**Arguments:**

- <b>`name`</b>:  Name of asset
- <b>`data`</b>:  Raw content
- <b>`content_type`</b>:  Content type (or mimetype) of asset
- <b>`wait`</b>:  Wait for asset to update

[**Link to source**](https://github.com/robocorp/robocorp/tree/master/storage/src/robocorp/storage/__init__.py#L261)

```python
set_bytes(
    name: str,
    data: bytes,
    content_type='application/octet-stream',
    wait: bool = True
)
```

# Exceptions

______________________________________________________________________

## `AssetNotFound`

No asset with given name/id found.

______________________________________________________________________

## `AssetUploadFailed`

There was an unexpected error while uploading an asset.
