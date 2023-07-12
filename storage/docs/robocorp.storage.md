<!-- markdownlint-disable -->

<a href="../../storage/src/robocorp/storage/__init__.py#L0"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square" /></a>

# <kbd>module</kbd> `robocorp.storage`




**Global Variables**
---------------
- **TYPE_CHECKING**
- **version_info**
- **KNOWN_MIMETYPES**

---

<a href="../../storage/src/robocorp/storage/__init__.py#L45"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square" /></a>

## <kbd>function</kbd> `list_assets`

```python
list_assets() → list[str]
```

List all the existing assets. 



**Returns:**
  A list of available assets' names 


---

<a href="../../storage/src/robocorp/storage/__init__.py#L54"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square" /></a>

## <kbd>function</kbd> `delete_asset`

```python
delete_asset(name: str)
```

Delete an asset by providing its `name`. 

This operation cannot be undone. 



**Args:**
 
 - <b>`name`</b>:  Asset to delete 



**Raises:**
 
 - <b>`AssetNotFound`</b>:  Asset with the given name does not exist 


---

<a href="../../storage/src/robocorp/storage/__init__.py#L94"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square" /></a>

## <kbd>function</kbd> `get_text`

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


---

<a href="../../storage/src/robocorp/storage/__init__.py#L110"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square" /></a>

## <kbd>function</kbd> `get_json`

```python
get_json(
    name: str,
    **kwargs
) → Union[dict[str, 'JSON'], list['JSON'], str, int, float, bool, NoneType]
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


---

<a href="../../storage/src/robocorp/storage/__init__.py#L128"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square" /></a>

## <kbd>function</kbd> `get_file`

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


---

<a href="../../storage/src/robocorp/storage/__init__.py#L153"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square" /></a>

## <kbd>function</kbd> `get_bytes`

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


---

<a href="../../storage/src/robocorp/storage/__init__.py#L184"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square" /></a>

## <kbd>function</kbd> `set_text`

```python
set_text(name: str, text: str, wait: bool = True)
```

Create or update an asset to contain the given string. 



**Arguments:**
 
 - <b>`name`</b>:  Name of asset 
 - <b>`text`</b>:  Text content for asset 
 - <b>`wait`</b>:  Wait for asset to update 


---

<a href="../../storage/src/robocorp/storage/__init__.py#L197"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square" /></a>

## <kbd>function</kbd> `set_json`

```python
set_json(
    name: str,
    value: Optional[dict[str, 'JSON'], list['JSON'], str, int, float, bool],
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


---

<a href="../../storage/src/robocorp/storage/__init__.py#L211"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square" /></a>

## <kbd>function</kbd> `set_file`

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
 - <b>`content_type`</b>:  Content type (or mimetype) of file, detected automatically  from file extension if not defined 
 - <b>`wait`</b>:  Wait for asset to update 


---

<a href="../../storage/src/robocorp/storage/__init__.py#L241"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square" /></a>

## <kbd>function</kbd> `set_bytes`

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




---

_This file was automatically generated via [lazydocs](https://github.com/ml-tooling/lazydocs)._
