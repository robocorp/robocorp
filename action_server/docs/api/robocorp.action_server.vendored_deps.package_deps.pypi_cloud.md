<!-- markdownlint-disable -->

# module `robocorp.action_server.vendored_deps.package_deps.pypi_cloud`

**Source:** [`pypi_cloud.py:0`](https://github.com/robocorp/robocorp/tree/master/action_server/src/robocorp/action_server/vendored_deps/package_deps/pypi_cloud.py#L0)

______________________________________________________________________

## class `PackageData`

**Source:** [`pypi_cloud.py:15`](https://github.com/robocorp/robocorp/tree/master/action_server/src/robocorp/action_server/vendored_deps/package_deps/pypi_cloud.py#L15)

### method `__init__`

**Source:** [`pypi_cloud.py:16`](https://github.com/robocorp/robocorp/tree/master/action_server/src/robocorp/action_server/vendored_deps/package_deps/pypi_cloud.py#L16)

```python
__init__(package_name: str, info: PyPiInfoTypedDict) → None
```

#### property `info`

#### property `latest_version`

______________________________________________________________________

### method `add_release`

**Source:** [`pypi_cloud.py:22`](https://github.com/robocorp/robocorp/tree/master/action_server/src/robocorp/action_server/vendored_deps/package_deps/pypi_cloud.py#L22)

```python
add_release(version_str: str, release_info: List[dict]) → None
```

**Args:**

- <b>`version_str`</b>:  The version we have info on.
- <b>`release_info`</b>:  For each release we may have a list of files available.

______________________________________________________________________

### method `get_last_release_data`

**Source:** [`pypi_cloud.py:51`](https://github.com/robocorp/robocorp/tree/master/action_server/src/robocorp/action_server/vendored_deps/package_deps/pypi_cloud.py#L51)

```python
get_last_release_data() → Optional[ReleaseData]
```

Provides the last release data (if there's any release).

______________________________________________________________________

### method `get_release_data`

**Source:** [`pypi_cloud.py:43`](https://github.com/robocorp/robocorp/tree/master/action_server/src/robocorp/action_server/vendored_deps/package_deps/pypi_cloud.py#L43)

```python
get_release_data(version: str) → Optional[ReleaseData]
```

______________________________________________________________________

### method `iter_versions_newer_than`

**Source:** [`pypi_cloud.py:87`](https://github.com/robocorp/robocorp/tree/master/action_server/src/robocorp/action_server/vendored_deps/package_deps/pypi_cloud.py#L87)

```python
iter_versions_newer_than(version: Versions) → Iterator[ReleaseData]
```

______________________________________________________________________

### method `iter_versions_released_after`

**Source:** [`pypi_cloud.py:57`](https://github.com/robocorp/robocorp/tree/master/action_server/src/robocorp/action_server/vendored_deps/package_deps/pypi_cloud.py#L57)

```python
iter_versions_released_after(
    after_datetime: Optional[datetime]
) → Iterator[ReleaseData]
```

**Args:**

- <b>`after_datetime`</b>:  if none all releases (except pre-releases) willbe provided.

______________________________________________________________________

## class `PyPiCloud`

**Source:** [`pypi_cloud.py:97`](https://github.com/robocorp/robocorp/tree/master/action_server/src/robocorp/action_server/vendored_deps/package_deps/pypi_cloud.py#L97)

### method `__init__`

**Source:** [`pypi_cloud.py:98`](https://github.com/robocorp/robocorp/tree/master/action_server/src/robocorp/action_server/vendored_deps/package_deps/pypi_cloud.py#L98)

```python
__init__(get_base_urls_weak_method: Optional[WeakMethod] = None) → None
```

______________________________________________________________________

### method `get_package_data`

**Source:** [`pypi_cloud.py:145`](https://github.com/robocorp/robocorp/tree/master/action_server/src/robocorp/action_server/vendored_deps/package_deps/pypi_cloud.py#L145)

```python
get_package_data(package_name: str) → Optional[PackageData]
```

______________________________________________________________________

### method `get_versions_newer_than`

**Source:** [`pypi_cloud.py:190`](https://github.com/robocorp/robocorp/tree/master/action_server/src/robocorp/action_server/vendored_deps/package_deps/pypi_cloud.py#L190)

```python
get_versions_newer_than(
    package_name: str,
    version: Union[Versions, str]
) → List[str]
```

**Args:**

- <b>`package_name`</b>:  The name of the package
- <b>`version`</b>:  The minimum version (versions returned must be > than this one).

**Returns:**
A sorted list containing the versions > than the one passed (the lastentry is the latest version).
