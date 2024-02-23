<!-- markdownlint-disable -->

# module `robocorp.log.pyproject_config`

**Source:** [`pyproject_config.py:0`](https://github.com/robocorp/robocorp/tree/master/log/src/robocorp/log/pyproject_config.py#L0)

This module contains functions to read a pyproject.toml file and  read the related tool.robocorp.log section.

______________________________________________________________________

## function `read_pyproject_toml`

**Source:** [`pyproject_config.py:19`](https://github.com/robocorp/robocorp/tree/master/log/src/robocorp/log/pyproject_config.py#L19)

```python
read_pyproject_toml(path: Path) → Optional[PyProjectInfo]
```

**Args:**
path: This is the path where the `pyproject.toml` file should be found. If it's not found directly in the given path, parent folders will be searched for the `pyproject.toml`.

**Returns:**
The information on the pyproject file (the toml contents and the actual path where the pyproject.toml was found).

______________________________________________________________________

## function `read_section_from_toml`

**Source:** [`pyproject_config.py:63`](https://github.com/robocorp/robocorp/tree/master/log/src/robocorp/log/pyproject_config.py#L63)

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

______________________________________________________________________

## function `read_robocorp_auto_log_config`

**Source:** [`pyproject_config.py:110`](https://github.com/robocorp/robocorp/tree/master/log/src/robocorp/log/pyproject_config.py#L110)

```python
read_robocorp_auto_log_config(
    context: IContextErrorReport,
    pyproject: PyProjectInfo
) → AutoLogConfigBase
```

**Args:**

- <b>`context`</b>:  The context used to report errors.
- <b>`pyproject`</b>:  The pyproject information from where the configuration should be loaded.

**Returns:**
The autolog configuration read from the given pyproject information.

______________________________________________________________________

## class `PyProjectInfo`

**Source:** [`pyproject_config.py:13`](https://github.com/robocorp/robocorp/tree/master/log/src/robocorp/log/pyproject_config.py#L13)

PyProjectInfo(pyproject: pathlib.Path, toml_contents: dict)

### method `__init__`

```python
__init__(pyproject: Path, toml_contents: dict) → None
```
