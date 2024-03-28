<!-- markdownlint-disable -->

# module `robocorp.log.pyproject_config`

This module contains functions to read a pyproject.toml file and  read the related tool.robocorp.log section.

# Functions

______________________________________________________________________

## `read_pyproject_toml`

**Args:**

- <b>`path`</b>:  This is the path where the `pyproject.toml` file should be found. If it's not found directly in the given path, parent folders will be searched for the `pyproject.toml`.

**Returns:**
The information on the pyproject file (the toml contents and the actualpath where the pyproject.toml was found).

[**Link to source**](https://github.com/robocorp/robocorp/tree/master/log/src/robocorp/log/pyproject_config.py#L19)

```python
read_pyproject_toml(path: Path) → Optional[PyProjectInfo]
```

______________________________________________________________________

## `read_section_from_toml`

**Args:**

- <b>`pyproject_info`</b>:  Information on the pyroject toml.
- <b>`section_name`</b>:  The name of the section to be read i.e.: tool.robocorp.log
- <b>`context`</b>:  The context used to report errors.

**Returns:**
The section which was read.

[**Link to source**](https://github.com/robocorp/robocorp/tree/master/log/src/robocorp/log/pyproject_config.py#L63)

```python
read_section_from_toml(
    pyproject_info: PyProjectInfo,
    section_name: str,
    context: Optional[IContextErrorReport] = None
) → Any
```

______________________________________________________________________

## `read_robocorp_auto_log_config`

**Args:**

- <b>`context`</b>:  The context used to report errors.
- <b>`pyproject`</b>:  The pyproject information from where the configuration should be loaded.

**Returns:**
The autolog configuration read from the given pyproject information.

[**Link to source**](https://github.com/robocorp/robocorp/tree/master/log/src/robocorp/log/pyproject_config.py#L110)

```python
read_robocorp_auto_log_config(
    context: IContextErrorReport,
    pyproject: PyProjectInfo
) → AutoLogConfigBase
```

______________________________________________________________________

# Class `PyProjectInfo`

PyProjectInfo(pyproject: pathlib.Path, toml_contents: dict)

### `__init__`

```python
__init__(pyproject: Path, toml_contents: dict) → None
```
