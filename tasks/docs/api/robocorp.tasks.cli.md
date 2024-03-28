<!-- markdownlint-disable -->

# module `robocorp.tasks.cli`

Main entry point for running tasks from robocorp-tasks.

Note that it's usually preferable to use `robocorp-tasks` as a command line tool, using it programmatically through the main(args) in this module is also possible.

Note: when running tasks, clients using this approach MUST make sure that any code which must be automatically logged is not imported prior the the `cli.main` call.

# Functions

______________________________________________________________________

## `main`

Entry point for running tasks from robocorp-tasks.

**Args:**

- <b>`args`</b>:  The command line arguments.

- <b>`exit`</b>:  Determines if the process should exit right after executing the command.

- <b>`plugin_manager`</b>:  Provides a way to customize internal functionality (should not be used by external clients in general).

**Returns:**
The exit code for the process.

[**Link to source**](https://github.com/robocorp/robocorp/tree/master/tasks/src/robocorp/tasks/cli.py#L91)

```python
main(
    args=None,
    exit: bool = True,
    argument_dispatcher: Optional[IArgumentsHandler] = None,
    plugin_manager: Optional[ForwardRef('_PluginManager')] = None
) → int
```

______________________________________________________________________

# Class `IArgumentsHandler`

## Methods

______________________________________________________________________

### `process_args`

**Args:**

- <b>`args`</b>:  The arguments to process.
- <b>`pm`</b>:  The plugin manager used to customize internal functionality.

Returns: the exitcode.

[**Link to source**](https://github.com/robocorp/robocorp/tree/master/tasks/src/robocorp/tasks/cli.py#L79)

```python
process_args(
    args: List[str],
    pm: Optional[ForwardRef('_PluginManager')] = None
) → int
```
