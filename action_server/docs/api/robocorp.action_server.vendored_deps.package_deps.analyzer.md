<!-- markdownlint-disable -->

# module `robocorp.action_server.vendored_deps.package_deps.analyzer`

**Source:** [`analyzer.py:0`](https://github.com/robocorp/robocorp/tree/master/action_server/src/robocorp/action_server/vendored_deps/package_deps/analyzer.py#L0)

This package should be independent of the rest as we can potentially make it a standalone package in the future (maybe with a command line UI).

______________________________________________________________________

## function `create_range_from_location`

**Source:** [`analyzer.py:58`](https://github.com/robocorp/robocorp/tree/master/action_server/src/robocorp/action_server/vendored_deps/package_deps/analyzer.py#L58)

```python
create_range_from_location(
    start_line: int,
    start_col: int,
    end_line: Optional[int] = None,
    end_col: Optional[int] = None
) → _RangeTypedDict
```

If the end_line and end_col aren't passed we consider that the location should go up until the end of the line.

______________________________________________________________________

## function `is_inside`

**Source:** [`analyzer.py:412`](https://github.com/robocorp/robocorp/tree/master/action_server/src/robocorp/action_server/vendored_deps/package_deps/analyzer.py#L412)

```python
is_inside(range_dct: _RangeTypedDict, line: int, col: int) → bool
```

______________________________________________________________________

## class `ScalarInfo`

**Source:** [`analyzer.py:24`](https://github.com/robocorp/robocorp/tree/master/action_server/src/robocorp/action_server/vendored_deps/package_deps/analyzer.py#L24)

### method `__init__`

**Source:** [`analyzer.py:25`](https://github.com/robocorp/robocorp/tree/master/action_server/src/robocorp/action_server/vendored_deps/package_deps/analyzer.py#L25)

```python
__init__(scalar: Any, location: Optional[Tuple[int, int, int, int]])
```

**Args:**
scalar:

- <b>`location`</b>:  tuple(start_line, start_col, end_line, end_col)

______________________________________________________________________

### method `as_range`

**Source:** [`analyzer.py:52`](https://github.com/robocorp/robocorp/tree/master/action_server/src/robocorp/action_server/vendored_deps/package_deps/analyzer.py#L52)

```python
as_range() → _RangeTypedDict
```

______________________________________________________________________

## class `LoaderWithLines`

**Source:** [`analyzer.py:86`](https://github.com/robocorp/robocorp/tree/master/action_server/src/robocorp/action_server/vendored_deps/package_deps/analyzer.py#L86)

______________________________________________________________________

### method `construct_scalar`

**Source:** [`analyzer.py:87`](https://github.com/robocorp/robocorp/tree/master/action_server/src/robocorp/action_server/vendored_deps/package_deps/analyzer.py#L87)

```python
construct_scalar(node, *args, **kwargs)
```

______________________________________________________________________

## class `Analyzer`

**Source:** [`analyzer.py:100`](https://github.com/robocorp/robocorp/tree/master/action_server/src/robocorp/action_server/vendored_deps/package_deps/analyzer.py#L100)

### method `__init__`

**Source:** [`analyzer.py:104`](https://github.com/robocorp/robocorp/tree/master/action_server/src/robocorp/action_server/vendored_deps/package_deps/analyzer.py#L104)

```python
__init__(
    contents: str,
    path: str,
    conda_cloud: ICondaCloud,
    pypi_cloud: Optional[IPyPiCloud] = None
)
```

**Args:**

- <b>`contents`</b>:  The contents of the conda.yaml/action-server.yaml.
- <b>`path`</b>:  The path for the conda yaml.

______________________________________________________________________

### method `find_conda_dep_at`

**Source:** [`analyzer.py:331`](https://github.com/robocorp/robocorp/tree/master/action_server/src/robocorp/action_server/vendored_deps/package_deps/analyzer.py#L331)

```python
find_conda_dep_at(line, col) → Optional[CondaDepInfo]
```

______________________________________________________________________

### method `find_pip_dep_at`

**Source:** [`analyzer.py:324`](https://github.com/robocorp/robocorp/tree/master/action_server/src/robocorp/action_server/vendored_deps/package_deps/analyzer.py#L324)

```python
find_pip_dep_at(line, col) → Optional[PipDepInfo]
```

______________________________________________________________________

### method `iter_conda_issues`

**Source:** [`analyzer.py:240`](https://github.com/robocorp/robocorp/tree/master/action_server/src/robocorp/action_server/vendored_deps/package_deps/analyzer.py#L240)

```python
iter_conda_issues() → Iterator[_DiagnosticsTypedDict]
```

______________________________________________________________________

### method `iter_issues`

**Source:** [`analyzer.py:191`](https://github.com/robocorp/robocorp/tree/master/action_server/src/robocorp/action_server/vendored_deps/package_deps/analyzer.py#L191)

```python
iter_issues() → Iterator[_DiagnosticsTypedDict]
```

______________________________________________________________________

### method `iter_pip_issues`

**Source:** [`analyzer.py:204`](https://github.com/robocorp/robocorp/tree/master/action_server/src/robocorp/action_server/vendored_deps/package_deps/analyzer.py#L204)

```python
iter_pip_issues()
```

______________________________________________________________________

### method `load_conda_yaml`

**Source:** [`analyzer.py:135`](https://github.com/robocorp/robocorp/tree/master/action_server/src/robocorp/action_server/vendored_deps/package_deps/analyzer.py#L135)

```python
load_conda_yaml() → None
```
