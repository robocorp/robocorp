<!-- markdownlint-disable -->

# module `robocorp.action_server.vendored_deps.package_deps.conda_cloud`

**Source:** [`conda_cloud.py:0`](https://github.com/robocorp/robocorp/tree/master/action_server/src/robocorp/action_server/vendored_deps/package_deps/conda_cloud.py#L0)

## Variables

- **TABLE_PACKAGES_SQL**
- **TABLE_VERSIONS_SQL**
- **CREATE_INDEXES_SQL**
- **INDEX_FOR_LIBRARIES**

______________________________________________________________________

## function `timestamp_to_datetime`

**Source:** [`conda_cloud.py:74`](https://github.com/robocorp/robocorp/tree/master/action_server/src/robocorp/action_server/vendored_deps/package_deps/conda_cloud.py#L74)

```python
timestamp_to_datetime(timestamp_milliseconds: float) → datetime
```

______________________________________________________________________

## function `version_key`

**Source:** [`conda_cloud.py:197`](https://github.com/robocorp/robocorp/tree/master/action_server/src/robocorp/action_server/vendored_deps/package_deps/conda_cloud.py#L197)

```python
version_key(version_info: CondaVersionInfo)
```

______________________________________________________________________

## function `sort_conda_version_infos`

**Source:** [`conda_cloud.py:204`](https://github.com/robocorp/robocorp/tree/master/action_server/src/robocorp/action_server/vendored_deps/package_deps/conda_cloud.py#L204)

```python
sort_conda_version_infos(
    versions: Union[Sequence[CondaVersionInfo], Set[CondaVersionInfo]]
) → List[CondaVersionInfo]
```

______________________________________________________________________

## function `version_str_key`

**Source:** [`conda_cloud.py:210`](https://github.com/robocorp/robocorp/tree/master/action_server/src/robocorp/action_server/vendored_deps/package_deps/conda_cloud.py#L210)

```python
version_str_key(version: str)
```

______________________________________________________________________

## function `sort_conda_versions`

**Source:** [`conda_cloud.py:217`](https://github.com/robocorp/robocorp/tree/master/action_server/src/robocorp/action_server/vendored_deps/package_deps/conda_cloud.py#L217)

```python
sort_conda_versions(versions: Union[Sequence[str], Set[str]]) → List[str]
```

______________________________________________________________________

## function `index_conda_info`

**Source:** [`conda_cloud.py:227`](https://github.com/robocorp/robocorp/tree/master/action_server/src/robocorp/action_server/vendored_deps/package_deps/conda_cloud.py#L227)

```python
index_conda_info(json_file: Path, target_sqlite_file: Path)
```

______________________________________________________________________

## enum `State`

**Source:** [`conda_cloud.py:68`](https://github.com/robocorp/robocorp/tree/master/action_server/src/robocorp/action_server/vendored_deps/package_deps/conda_cloud.py#L68)

An enumeration.

### Values

- **initial** = 1
- **downloading** = 2
- **done** = 3

______________________________________________________________________

## class `SqliteQueries`

**Source:** [`conda_cloud.py:79`](https://github.com/robocorp/robocorp/tree/master/action_server/src/robocorp/action_server/vendored_deps/package_deps/conda_cloud.py#L79)

### method `__init__`

**Source:** [`conda_cloud.py:80`](https://github.com/robocorp/robocorp/tree/master/action_server/src/robocorp/action_server/vendored_deps/package_deps/conda_cloud.py#L80)

```python
__init__(sqlite_file: Union[Path, Sequence[Path]])
```

______________________________________________________________________

### method `db_cursors`

**Source:** [`db_cursors:88`](https://github.com/robocorp/robocorp/tree/master/action_server/robocorp/action_server/vendored_deps/package_deps/conda_cloud/db_cursors#L88)

```python
db_cursors(
    db_cursor: Optional[Sequence[object]] = None
) → Iterator[Sequence[object]]
```

______________________________________________________________________

### method `query_names`

**Source:** [`conda_cloud.py:118`](https://github.com/robocorp/robocorp/tree/master/action_server/src/robocorp/action_server/vendored_deps/package_deps/conda_cloud.py#L118)

```python
query_names(db_cursors: Optional[Sequence[object]] = None) → Set[str]
```

______________________________________________________________________

### method `query_version_info`

**Source:** [`conda_cloud.py:154`](https://github.com/robocorp/robocorp/tree/master/action_server/src/robocorp/action_server/vendored_deps/package_deps/conda_cloud.py#L154)

```python
query_version_info(
    package_name: str,
    version: str,
    db_cursors: Optional[Sequence[object]] = None
) → CondaVersionInfo
```

Note that the same package/version may have multiple infos because of build ids (but in this API this isn't given, so, if the same depends are available then they're shown only as one).

______________________________________________________________________

### method `query_versions`

**Source:** [`conda_cloud.py:128`](https://github.com/robocorp/robocorp/tree/master/action_server/src/robocorp/action_server/vendored_deps/package_deps/conda_cloud.py#L128)

```python
query_versions(
    package_name,
    db_cursors: Optional[Sequence[object]] = None
) → Set[str]
```

______________________________________________________________________

## class `CondaCloud`

**Source:** [`conda_cloud.py:454`](https://github.com/robocorp/robocorp/tree/master/action_server/src/robocorp/action_server/vendored_deps/package_deps/conda_cloud.py#L454)

Manages information from conda.

The cache_dir is where we hold information on disk.

The basic structure is: /cache_dir/cache_dir/tmp_0001 \<-- used to download information and build the sqlite db./cache_dir/tmp_0001/noarch.json \<-- actually removed after the sqlite db is built./cache_dir/tmp_0001/win-64.json/cache_dir/index_0001/noarch.db \<-- sqlite db we actually use/cache_dir/index_0001/win-64.db/cache_dir/latest_index_info.json \<-- will be used to point to index_0001

### method `__init__`

**Source:** [`conda_cloud.py:470`](https://github.com/robocorp/robocorp/tree/master/action_server/src/robocorp/action_server/vendored_deps/package_deps/conda_cloud.py#L470)

```python
__init__(cache_dir: Path, reindex_if_old: bool = True) → None
```

______________________________________________________________________

### method `is_information_cached`

**Source:** [`conda_cloud.py:684`](https://github.com/robocorp/robocorp/tree/master/action_server/src/robocorp/action_server/vendored_deps/package_deps/conda_cloud.py#L684)

```python
is_information_cached() → bool
```

______________________________________________________________________

### method `load_latest_index_info`

**Source:** [`conda_cloud.py:641`](https://github.com/robocorp/robocorp/tree/master/action_server/src/robocorp/action_server/vendored_deps/package_deps/conda_cloud.py#L641)

```python
load_latest_index_info() → Optional[LatestIndexInfoTypedDict]
```

______________________________________________________________________

### method `schedule_update`

**Source:** [`conda_cloud.py:530`](https://github.com/robocorp/robocorp/tree/master/action_server/src/robocorp/action_server/vendored_deps/package_deps/conda_cloud.py#L530)

```python
schedule_update(
    on_finished: Optional[IOnFinished] = None,
    wait=False,
    force=False
) → None
```

This can be called at any time (in any thread). It schedules the download of the information we need.

If it's currently downloading already it'll not do a new request and if it was already downloaded it'll only redownload if force == True.

______________________________________________________________________

### method `sqlite_queries`

**Source:** [`conda_cloud.py:695`](https://github.com/robocorp/robocorp/tree/master/action_server/src/robocorp/action_server/vendored_deps/package_deps/conda_cloud.py#L695)

```python
sqlite_queries() → Optional[SqliteQueries]
```
