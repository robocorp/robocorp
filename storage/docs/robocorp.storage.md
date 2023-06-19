<!-- markdownlint-disable -->

<a href="../../storage/src/robocorp/storage/__init__.py#L0"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square" /></a>

# <kbd>module</kbd> `robocorp.storage`




**Global Variables**
---------------
- **version_info**

---

<a href="../../storage/src/robocorp/storage/__init__.py#L16"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square" /></a>

## <kbd>function</kbd> `list_assets`

```python
list_assets() → List[Dict[str, str]]
```

List all the existing assets. 



**Returns:**
  A list of assets where each asset is a dictionary with fields like 'id' and  'name'. 


---

<a href="../../storage/src/robocorp/storage/__init__.py#L70"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square" /></a>

## <kbd>function</kbd> `get_asset`

```python
get_asset(name: str) → str
```

Get the asset's value by providing its `name`. 



**Args:**
 
 - <b>`name`</b>:  Name of the asset to fetch. 



**Returns:**
 The previously set value of this asset. (empty if it was never set) 



**Raises:**
 
 - <b>`AssetNotFound`</b>:  When the queried asset doesn't exist. 


---

<a href="../../storage/src/robocorp/storage/__init__.py#L100"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square" /></a>

## <kbd>function</kbd> `set_asset`

```python
set_asset(name: str, value: str, wait: bool = True)
```

Sets/Creates an asset named `name` with the provided `value`. 



**Args:**
 
 - <b>`name`</b>:  Name of the existing or new asset to create. (if missing) 
 - <b>`value`</b>:  The new value set within the asset. 
 - <b>`wait`</b>:  Blocks until the new value is reflected within the asset. 



**Raises:**
 
 - <b>`AssetNotFound`</b>:  When the queried asset doesn't exist. 


---

<a href="../../storage/src/robocorp/storage/__init__.py#L149"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square" /></a>

## <kbd>function</kbd> `delete_asset`

```python
delete_asset(name: str)
```

Delete an asset by providing its `name`. 



**Args:**
 
 - <b>`name`</b>:  Name of the asset to delete. 



**Raises:**
 
 - <b>`AssetNotFound`</b>:  When the queried asset doesn't exist. 




---

_This file was automatically generated via [lazydocs](https://github.com/ml-tooling/lazydocs)._
