<!-- markdownlint-disable -->

<a href="../../log/src/robocorp/log/pyproject_config.py#L0"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square" /></a>

# <kbd>module</kbd> `robocorp.log.pyproject_config`
This module contains functions to read a pyproject.toml file and  read the related tool.robocorp.log section. 


---

<a href="../../log/src/robocorp/log/pyproject_config.py#L19"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square" /></a>

## <kbd>function</kbd> `read_pyproject_toml`

```python
read_pyproject_toml(path: Path) → Optional[PyProjectInfo]
```



**Args:**
 path:  This is the path where the `pyproject.toml` file should be found.  If it's not found directly in the given path, parent folders will  be searched for the `pyproject.toml`. 



**Returns:**
 The information on the pyproject file (the toml contents and the actual  path where the pyproject.toml was found). 


---

<a href="../../log/src/robocorp/log/pyproject_config.py#L63"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square" /></a>

## <kbd>function</kbd> `read_section_from_toml`

```python
read_section_from_toml(
    pyproject_info: PyProjectInfo,
    section_name: str,
    context: Optional[IContextErrorReport] = None
) → Any
```



**Args:**

 - <b>`pyproject_info`</b>:  Information on the pyroject toml. 
 - <b>`section_name`</b>:  The name of the section to be read 
 - <b>`i.e.`</b>:  tool.robocorp.log 
 - <b>`context`</b>:  The context used to report errors. 



**Returns:**
The section which was read. 


---

<a href="../../log/src/robocorp/log/pyproject_config.py#L110"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square" /></a>

## <kbd>function</kbd> `read_robocorp_auto_log_config`

```python
read_robocorp_auto_log_config(
    context: IContextErrorReport,
    pyproject: PyProjectInfo
) → AutoLogConfigBase
```



**Args:**

 - <b>`context`</b>:  The context used to report errors. 
 - <b>`pyproject`</b>:  The pyproject information from where the configuration should  be loaded. 



**Returns:**
The autolog configuration read from the given pyproject information. 


---

<a href="../../log/src/robocorp/log/pyproject_config.py#L13"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square" /></a>

## <kbd>class</kbd> `PyProjectInfo`
PyProjectInfo(pyproject: pathlib.Path, toml_contents: dict) 

<a href="../../log/<string>"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square" /></a>

### <kbd>function</kbd> `__init__`

```python
__init__(pyproject: Path, toml_contents: dict) → None
```











---

_This file was automatically generated via [lazydocs](https://github.com/ml-tooling/lazydocs)._
