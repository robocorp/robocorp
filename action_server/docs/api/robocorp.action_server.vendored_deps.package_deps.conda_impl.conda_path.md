<!-- markdownlint-disable -->

# module `robocorp.action_server.vendored_deps.package_deps.conda_impl.conda_path`

**Source:** [`conda_path.py:0`](https://github.com/robocorp/robocorp/tree/master/action_server/src/robocorp/action_server/vendored_deps/package_deps/conda_impl/conda_path.py#L0)

## Variables

- **on_win**
- **PATH_MATCH_REGEX**
- **KNOWN_EXTENSIONS**

______________________________________________________________________

## function `is_path`

**Source:** [`conda_path.py:40`](https://github.com/robocorp/robocorp/tree/master/action_server/src/robocorp/action_server/vendored_deps/package_deps/conda_impl/conda_path.py#L40)

```python
is_path(value)
```

______________________________________________________________________

## function `expand`

**Source:** [`conda_path.py:46`](https://github.com/robocorp/robocorp/tree/master/action_server/src/robocorp/action_server/vendored_deps/package_deps/conda_impl/conda_path.py#L46)

```python
expand(path)
```

______________________________________________________________________

## function `paths_equal`

**Source:** [`conda_path.py:50`](https://github.com/robocorp/robocorp/tree/master/action_server/src/robocorp/action_server/vendored_deps/package_deps/conda_impl/conda_path.py#L50)

```python
paths_equal(path1, path2)
```

**Examples:**

` paths_equal('/a/b/c', '/a/b/c/d/..')`
True

______________________________________________________________________

## function `tokenized_startswith`

**Source:** [`conda_path.py:91`](https://github.com/robocorp/robocorp/tree/master/action_server/src/robocorp/action_server/vendored_deps/package_deps/conda_impl/conda_path.py#L91)

```python
tokenized_startswith(test_iterable, startswith_iterable)
```

______________________________________________________________________

## function `pyc_path`

**Source:** [`conda_path.py:95`](https://github.com/robocorp/robocorp/tree/master/action_server/src/robocorp/action_server/vendored_deps/package_deps/conda_impl/conda_path.py#L95)

```python
pyc_path(py_path, python_major_minor_version)
```

This must not return backslashes on Windows as that will break tests and leads to an eventual need to make url_to_path return backslashes too and that may end up changing files on disc or to the result of comparisons with the contents of them.

______________________________________________________________________

## function `missing_pyc_files`

**Source:** [`conda_path.py:114`](https://github.com/robocorp/robocorp/tree/master/action_server/src/robocorp/action_server/vendored_deps/package_deps/conda_impl/conda_path.py#L114)

```python
missing_pyc_files(python_major_minor_version, files)
```

______________________________________________________________________

## function `parse_entry_point_def`

**Source:** [`conda_path.py:124`](https://github.com/robocorp/robocorp/tree/master/action_server/src/robocorp/action_server/vendored_deps/package_deps/conda_impl/conda_path.py#L124)

```python
parse_entry_point_def(ep_definition)
```

______________________________________________________________________

## function `get_python_short_path`

**Source:** [`conda_path.py:131`](https://github.com/robocorp/robocorp/tree/master/action_server/src/robocorp/action_server/vendored_deps/package_deps/conda_impl/conda_path.py#L131)

```python
get_python_short_path(python_version=None)
```

______________________________________________________________________

## function `get_python_site_packages_short_path`

**Source:** [`conda_path.py:139`](https://github.com/robocorp/robocorp/tree/master/action_server/src/robocorp/action_server/vendored_deps/package_deps/conda_impl/conda_path.py#L139)

```python
get_python_site_packages_short_path(python_version)
```

______________________________________________________________________

## function `get_major_minor_version`

**Source:** [`conda_path.py:152`](https://github.com/robocorp/robocorp/tree/master/action_server/src/robocorp/action_server/vendored_deps/package_deps/conda_impl/conda_path.py#L152)

```python
get_major_minor_version(string, with_dot=True)
```

______________________________________________________________________

## function `get_bin_directory_short_path`

**Source:** [`conda_path.py:188`](https://github.com/robocorp/robocorp/tree/master/action_server/src/robocorp/action_server/vendored_deps/package_deps/conda_impl/conda_path.py#L188)

```python
get_bin_directory_short_path()
```

______________________________________________________________________

## function `win_path_ok`

**Source:** [`conda_path.py:192`](https://github.com/robocorp/robocorp/tree/master/action_server/src/robocorp/action_server/vendored_deps/package_deps/conda_impl/conda_path.py#L192)

```python
win_path_ok(path)
```

______________________________________________________________________

## function `win_path_double_escape`

**Source:** [`conda_path.py:196`](https://github.com/robocorp/robocorp/tree/master/action_server/src/robocorp/action_server/vendored_deps/package_deps/conda_impl/conda_path.py#L196)

```python
win_path_double_escape(path)
```

______________________________________________________________________

## function `win_path_backout`

**Source:** [`conda_path.py:200`](https://github.com/robocorp/robocorp/tree/master/action_server/src/robocorp/action_server/vendored_deps/package_deps/conda_impl/conda_path.py#L200)

```python
win_path_backout(path)
```

______________________________________________________________________

## function `ensure_pad`

**Source:** [`conda_path.py:207`](https://github.com/robocorp/robocorp/tree/master/action_server/src/robocorp/action_server/vendored_deps/package_deps/conda_impl/conda_path.py#L207)

```python
ensure_pad(name, pad='_')
```

**Examples:**

` ensure_pad('conda')`
'_conda_'
` ensure_pad('_conda')`'\__conda_'
` ensure_pad('')`
''

______________________________________________________________________

## function `is_private_env_name`

**Source:** [`conda_path.py:225`](https://github.com/robocorp/robocorp/tree/master/action_server/src/robocorp/action_server/vendored_deps/package_deps/conda_impl/conda_path.py#L225)

```python
is_private_env_name(env_name)
```

**Examples:**

` is_private_env_name("_conda")`
False
` is_private_env_name("_conda_")`True

______________________________________________________________________

## function `is_private_env_path`

**Source:** [`conda_path.py:238`](https://github.com/robocorp/robocorp/tree/master/action_server/src/robocorp/action_server/vendored_deps/package_deps/conda_impl/conda_path.py#L238)

```python
is_private_env_path(env_path)
```

**Examples:**

` is_private_env_path('/some/path/to/envs/_conda_')`
True
` is_private_env_path('/not/an/envs_dir/_conda_')`False

______________________________________________________________________

## function `right_pad_os_sep`

**Source:** [`conda_path.py:256`](https://github.com/robocorp/robocorp/tree/master/action_server/src/robocorp/action_server/vendored_deps/package_deps/conda_impl/conda_path.py#L256)

```python
right_pad_os_sep(path)
```

______________________________________________________________________

## function `split_filename`

**Source:** [`conda_path.py:260`](https://github.com/robocorp/robocorp/tree/master/action_server/src/robocorp/action_server/vendored_deps/package_deps/conda_impl/conda_path.py#L260)

```python
split_filename(path_or_url)
```

______________________________________________________________________

## function `get_python_noarch_target_path`

**Source:** [`conda_path.py:265`](https://github.com/robocorp/robocorp/tree/master/action_server/src/robocorp/action_server/vendored_deps/package_deps/conda_impl/conda_path.py#L265)

```python
get_python_noarch_target_path(
    source_short_path,
    target_site_packages_short_path
)
```

______________________________________________________________________

## function `strip_pkg_extension`

**Source:** [`conda_path.py:276`](https://github.com/robocorp/robocorp/tree/master/action_server/src/robocorp/action_server/vendored_deps/package_deps/conda_impl/conda_path.py#L276)

```python
strip_pkg_extension(path: 'str')
```

**Examples:**

` strip_pkg_extension("/path/_license-1.1-py27_1.tar.bz2")`
('/path/\_license-1.1-py27_1', '.tar.bz2')
` strip_pkg_extension("/path/_license-1.1-py27_1.conda")`('/path/\_license-1.1-py27_1', '.conda')
` strip_pkg_extension("/path/_license-1.1-py27_1")`
('/path/\_license-1.1-py27_1', None)

______________________________________________________________________

## function `is_package_file`

**Source:** [`conda_path.py:294`](https://github.com/robocorp/robocorp/tree/master/action_server/src/robocorp/action_server/vendored_deps/package_deps/conda_impl/conda_path.py#L294)

```python
is_package_file(path)
```

**Examples:**

` is_package_file("/path/_license-1.1-py27_1.tar.bz2")`
True
` is_package_file("/path/_license-1.1-py27_1.conda")`True
` is_package_file("/path/_license-1.1-py27_1")`
False
