<!-- markdownlint-disable -->

# module `robocorp.actions.cli`

**Source:** [`cli.py:0`](https://github.com/robocorp/robocorp/tree/master/actions/src/robocorp/actions/cli.py#L0)

______________________________________________________________________

## function `main`

**Source:** [`cli.py:12`](https://github.com/robocorp/robocorp/tree/master/actions/src/robocorp/actions/cli.py#L12)

```python
main(
    args=None,
    exit: bool = True,
    plugin_manager: Optional[ForwardRef('_PluginManager')] = None
) → int
```

Entry point for running actions from robocorp-actions.

**Args:**

- <b>`args`</b>:  The command line arguments.

- <b>`exit`</b>:  Determines if the process should exit right after executing the command.

plugin_manager: Provides a way to customize internal functionality (should not be used by external clients in general).

**Returns:**
The exit code for the process.
