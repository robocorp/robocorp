<!-- markdownlint-disable -->

# module `robocorp.storage`

**Source:** [`__init__.py:0`](https://github.com/robocorp/robo/tree/master/storage/src/robocorp/storage/__init__.py#L0)

______________________________________________________________________

## function `list_assets`

**Source:** [`__init__.py:45`](https://github.com/robocorp/robo/tree/master/storage/src/robocorp/storage/__init__.py#L45)

```python
list_assets(page_limit: Optional[int] = 100) → List[str]
```

List all the existing assets.

**Args:**

- <b>`page_limit`</b>:  How many assets to retrieve per request

**Returns:**
A list of available assets' names

______________________________________________________________________

## function `delete_asset`

**Source:** [`__init__.py:77`](https://github.com/robocorp/robo/tree/master/storage/src/robocorp/storage/__init__.py#L77)

```python
delete_asset(name: str)
```

Delete an asset by providing its `name`.

This operation cannot be undone.

**Args:**

- <b>`name`</b>:  Asset to delete

**Raises:**

- <b>`AssetNotFound`</b>:  Asset with the given name does not exist

______________________________________________________________________

## function `get_text`

**Source:** [`__init__.py:117`](https://github.com/robocorp/robo/tree/master/storage/src/robocorp/storage/__init__.py#L117)

```python
get_text(name: str) → str
```

Return the given asset as text.

**Arguments:**

- <b>`name`</b>:  Name of asset

**Returns:**
Asset content as text

**Raises:**

- <b>`AssetNotFound`</b>:  No asset defined with given name

______________________________________________________________________

## function `get_json`

**Source:** [`__init__.py:133`](https://github.com/robocorp/robo/tree/master/storage/src/robocorp/storage/__init__.py#L133)

```python
get_json(
    name: str,
    **kwargs
) → Union[Dict[str, ForwardRef('JSON')], List[ForwardRef('JSON')], str, int, float, bool, NoneType]
```

Return the given asset as a deserialized JSON object.

**Arguments:**

- <b>`name`</b>:  Name of asset
- <b>`**kwargs`</b>:  Additional parameters for `json.loads`

**Returns:**
Asset content as a Python object (dict, list etc.)

**Raises:**

- <b>`AssetNotFound`</b>:  No asset defined with given name
- <b>`JSONDecodeError`</b>:  Asset was not valid JSON

______________________________________________________________________

## function `get_file`

**Source:** [`__init__.py:151`](https://github.com/robocorp/robo/tree/master/storage/src/robocorp/storage/__init__.py#L151)

```python
get_file(name: str, path: Union[PathLike, str], exist_ok=False) → Path
```

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

______________________________________________________________________

## function `get_bytes`

**Source:** [`__init__.py:176`](https://github.com/robocorp/robo/tree/master/storage/src/robocorp/storage/__init__.py#L176)

```python
get_bytes(name: str) → bytes
```

Return the given asset as bytes.

**Arguments:**

- <b>`name`</b>:  Name of asset

**Returns:**
Asset content as bytes

**Raises:**

- <b>`AssetNotFound`</b>:  No asset defined with given name

______________________________________________________________________

## function `set_text`

**Source:** [`__init__.py:207`](https://github.com/robocorp/robo/tree/master/storage/src/robocorp/storage/__init__.py#L207)

```python
set_text(name: str, text: str, wait: bool = True)
```

Create or update an asset to contain the given string.

**Arguments:**

- <b>`name`</b>:  Name of asset
- <b>`text`</b>:  Text content for asset
- <b>`wait`</b>:  Wait for asset to update

______________________________________________________________________

## function `set_json`

**Source:** [`__init__.py:220`](https://github.com/robocorp/robo/tree/master/storage/src/robocorp/storage/__init__.py#L220)

```python
set_json(
    name: str,
    value: Optional[Dict[str, ForwardRef('JSON')], List[ForwardRef('JSON')], str, int, float, bool],
    wait: bool = True,
    **kwargs
)
```

Create or update an asset to contain the given object, serialized as JSON.

**Arguments:**

- <b>`name`</b>:  Name of asset
- <b>`value`</b>:  Value for asset, e.g. dict or list
- <b>`wait`</b>:  Wait for asset to update
- <b>`**kwargs`</b>:  Additional arguments for `json.dumps`

______________________________________________________________________

## function `set_file`

**Source:** [`__init__.py:234`](https://github.com/robocorp/robo/tree/master/storage/src/robocorp/storage/__init__.py#L234)

```python
set_file(
    name: str,
    path: Union[PathLike, str],
    content_type: Optional[str] = None,
    wait: bool = True
)
```

Create or update an asset to contain the contents of the given file.

**Arguments:**

- <b>`name`</b>:  Name of asset
- <b>`path`</b>:  Path to file
- <b>`content_type`</b>:  Content type (or mimetype) of file, detected automatically from file extension if not defined
- <b>`wait`</b>:  Wait for asset to update

______________________________________________________________________

## function `set_bytes`

**Source:** [`__init__.py:264`](https://github.com/robocorp/robo/tree/master/storage/src/robocorp/storage/__init__.py#L264)

```python
set_bytes(
    name: str,
    data: bytes,
    content_type='application/octet-stream',
    wait: bool = True
)
```

Create or update an asset to contain the given bytes.

**Arguments:**

- <b>`name`</b>:  Name of asset
- <b>`data`</b>:  Raw content
- <b>`content_type`</b>:  Content type (or mimetype) of asset
- <b>`wait`</b>:  Wait for asset to update

______________________________________________________________________

## exception `AssetNotFound`

**Source:** [`_client.py:30`](https://github.com/robocorp/robo/tree/master/storage/src/robocorp/storage/_client.py#L30)

No asset with given name/id found.

______________________________________________________________________

## exception `AssetUploadFailed`

**Source:** [`_client.py:34`](https://github.com/robocorp/robo/tree/master/storage/src/robocorp/storage/_client.py#L34)

There was an unexpected error while uploading an asset.
