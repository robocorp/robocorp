<!-- markdownlint-disable -->

# module `robocorp.action_server.vendored_deps.package_deps.pip_impl.pip_distlib_util`

**Source:** [`pip_distlib_util.py:0`](https://github.com/robocorp/robocorp/tree/master/action_server/src/robocorp/action_server/vendored_deps/package_deps/pip_impl/pip_distlib_util.py#L0)

______________________________________________________________________

## function `parse_marker`

**Source:** [`pip_distlib_util.py:20`](https://github.com/robocorp/robocorp/tree/master/action_server/src/robocorp/action_server/vendored_deps/package_deps/pip_impl/pip_distlib_util.py#L20)

```python
parse_marker(marker_string)
```

Parse a marker string and return a dictionary containing a marker expression.

The dictionary will contain keys "op", "lhs" and "rhs" for non-terminals in the expression grammar, or strings. A string contained in quotes is to be interpreted as a literal string, and a string not contained in quotes is a variable (such as os_name).

______________________________________________________________________

## function `parse_requirement`

**Source:** [`pip_distlib_util.py:110`](https://github.com/robocorp/robocorp/tree/master/action_server/src/robocorp/action_server/vendored_deps/package_deps/pip_impl/pip_distlib_util.py#L110)

```python
parse_requirement(req)
```

Parse a requirement passed in as a string. Return a Container whose attributes contain the various parts of the requirement.
