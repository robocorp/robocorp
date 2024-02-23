<!-- markdownlint-disable -->

# module `robocorp.action_server.vendored_deps.package_deps.pip_impl.pip_packaging_version`

**Source:** [`pip_packaging_version.py:0`](https://github.com/robocorp/robocorp/tree/master/action_server/src/robocorp/action_server/vendored_deps/package_deps/pip_impl/pip_packaging_version.py#L0)

## Variables

- **VERSION_PATTERN**

______________________________________________________________________

## function `parse`

**Source:** [`pip_packaging_version.py:47`](https://github.com/robocorp/robocorp/tree/master/action_server/src/robocorp/action_server/vendored_deps/package_deps/pip_impl/pip_packaging_version.py#L47)

```python
parse(version: str) → Union[ForwardRef('LegacyVersion'), ForwardRef('Version')]
```

Parse the given version string and return either a :class:`Version` object or a :class:`LegacyVersion` object depending on if the given version is a valid PEP 440 version or a legacy version.

______________________________________________________________________

## class `Version`

**Source:** [`pip_packaging_version.py:261`](https://github.com/robocorp/robocorp/tree/master/action_server/src/robocorp/action_server/vendored_deps/package_deps/pip_impl/pip_packaging_version.py#L261)

### method `__init__`

**Source:** [`pip_packaging_version.py:264`](https://github.com/robocorp/robocorp/tree/master/action_server/src/robocorp/action_server/vendored_deps/package_deps/pip_impl/pip_packaging_version.py#L264)

```python
__init__(version: str) → None
```

#### property `base_version`

#### property `dev`

#### property `epoch`

#### property `is_devrelease`

#### property `is_postrelease`

#### property `is_prerelease`

#### property `local`

#### property `major`

#### property `micro`

#### property `minor`

#### property `post`

#### property `pre`

#### property `public`

#### property `release`

______________________________________________________________________

## class `LegacyVersion`

**Source:** [`pip_packaging_version.py:111`](https://github.com/robocorp/robocorp/tree/master/action_server/src/robocorp/action_server/vendored_deps/package_deps/pip_impl/pip_packaging_version.py#L111)

### method `__init__`

**Source:** [`pip_packaging_version.py:112`](https://github.com/robocorp/robocorp/tree/master/action_server/src/robocorp/action_server/vendored_deps/package_deps/pip_impl/pip_packaging_version.py#L112)

```python
__init__(version: str) → None
```

#### property `base_version`

#### property `dev`

#### property `epoch`

#### property `is_devrelease`

#### property `is_postrelease`

#### property `is_prerelease`

#### property `local`

#### property `post`

#### property `pre`

#### property `public`

#### property `release`

______________________________________________________________________

## exception `InvalidVersion`

**Source:** [`pip_packaging_version.py:59`](https://github.com/robocorp/robocorp/tree/master/action_server/src/robocorp/action_server/vendored_deps/package_deps/pip_impl/pip_packaging_version.py#L59)

An invalid version was found, users should refer to PEP 440.
