<!-- markdownlint-disable -->

# module `robocorp.tasks.cli`

**Source:** [`cli:0`](https://github.com/robocorp/robocorp/tree/master/tasks/robocorp/tasks/cli#L0)

Main entry point for running tasks from robocorp-tasks.

Note that it's usually preferable to use `robocorp-tasks` as a command line tool, using it programmatically through the main(args) in this module is also possible.

Note: when running tasks, clients using this approach MUST make sure that any code which must be automatically logged is not imported prior the the `cli.main` call.

______________________________________________________________________

## function `main`

**Source:** [`main:46`](https://github.com/robocorp/robocorp/tree/master/tasks/robocorp/tasks/cli/main#L46)

```python
main(
    args=None,
    exit: bool = True,
    argument_dispatcher: Optional[IArgumentsHandler] = None
) → int
```

Entry point for running tasks from robocorp-tasks.

______________________________________________________________________

## class `IArgumentsHandler`

**Source:** [`IArgumentsHandler:36`](https://github.com/robocorp/robocorp/tree/master/tasks/robocorp/tasks/cli/IArgumentsHandler#L36)

______________________________________________________________________

### method `process_args`

**Source:** [`process_args:37`](https://github.com/robocorp/robocorp/tree/master/tasks/robocorp/tasks/cli/process_args#L37)

```python
process_args(args: List[str]) → int
```

**Args:**

- <b>`args`</b>:  The arguments to process.

Returns: the exitcode.
