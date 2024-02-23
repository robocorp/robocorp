<!-- markdownlint-disable -->

# module `robocorp.action_server.vendored_deps.action_package_handling`

**Source:** [`__init__.py:0`](https://github.com/robocorp/robocorp/tree/master/action_server/src/robocorp/action_server/vendored_deps/action_package_handling/__init__.py#L0)

## Variables

- **cli_errors**

______________________________________________________________________

## function `convert_conda_entry`

**Source:** [`__init__.py:46`](https://github.com/robocorp/robocorp/tree/master/action_server/src/robocorp/action_server/vendored_deps/action_package_handling/__init__.py#L46)

```python
convert_conda_entry(package_yaml: Path, entry: str) → Tuple[str, str]
```

______________________________________________________________________

## function `convert_pip_entry`

**Source:** [`__init__.py:60`](https://github.com/robocorp/robocorp/tree/master/action_server/src/robocorp/action_server/vendored_deps/action_package_handling/__init__.py#L60)

```python
convert_pip_entry(package_yaml: Path, entry: str) → Tuple[str, str]
```

______________________________________________________________________

## function `update_package`

**Source:** [`__init__.py:234`](https://github.com/robocorp/robocorp/tree/master/action_server/src/robocorp/action_server/vendored_deps/action_package_handling/__init__.py#L234)

```python
update_package(
    cwd: Path,
    dry_run: bool,
    backup: bool = True,
    stream=None
) → None
```

Updates a given package to conform to the latest structure.

Current operations done: Convert conda.yaml or action-server.yaml to package.yaml

**Args:**

- <b>`cwd`</b>:  This is the directory where the action package is
- <b>`(i.e.`</b>:  the directory with package.yaml or some older versionhaving conda.yaml or action-server.yaml).

______________________________________________________________________

## function `create_hash`

**Source:** [`__init__.py:261`](https://github.com/robocorp/robocorp/tree/master/action_server/src/robocorp/action_server/vendored_deps/action_package_handling/__init__.py#L261)

```python
create_hash(contents: str) → str
```

______________________________________________________________________

## function `create_conda_contents_from_package_yaml_contents`

**Source:** [`__init__.py:269`](https://github.com/robocorp/robocorp/tree/master/action_server/src/robocorp/action_server/vendored_deps/action_package_handling/__init__.py#L269)

```python
create_conda_contents_from_package_yaml_contents(
    package_yaml: Path,
    package_yaml_contents: dict
) → dict
```

______________________________________________________________________

## function `create_conda_from_package_yaml`

**Source:** [`__init__.py:389`](https://github.com/robocorp/robocorp/tree/master/action_server/src/robocorp/action_server/vendored_deps/action_package_handling/__init__.py#L389)

```python
create_conda_from_package_yaml(datadir: Path, package_yaml: Path) → Path
```

**Args:**

- <b>`package_yaml`</b>:  This is the package.yaml from which the conda.yaml (to be supplied to rcc to create the env) should be created.

- <b>`package_yaml_contents`</b>:  If specified this are the yaml-loaded contents of the package yaml.

Returns: The path to the generated conda.yaml.
