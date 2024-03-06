<!-- markdownlint-disable -->

# module `robocorp.tasks.cli`

**Source:** [`cli.py:0`](https://github.com/robocorp/robocorp/tree/master/tasks/src/robocorp/tasks/cli.py#L0)

Main entry point for running tasks from robocorp-tasks.

Note that it's usually preferable to use `robocorp-tasks` as a command line tool, using it programmatically through the main(args) in this module is also possible.

Note: when running tasks, clients using this approach MUST make sure that any code which must be automatically logged is not imported prior the the `cli.main` call.

______________________________________________________________________

## function `inject_truststore`

**Source:** [`cli.py:18`](https://github.com/robocorp/robocorp/tree/master/tasks/src/robocorp/tasks/cli.py#L18)

```python
inject_truststore()
```

______________________________________________________________________

## function `main`

**Source:** [`cli.py:63`](https://github.com/robocorp/robocorp/tree/master/tasks/src/robocorp/tasks/cli.py#L63)

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

**Source:** [`cli.py:53`](https://github.com/robocorp/robocorp/tree/master/tasks/src/robocorp/tasks/cli.py#L53)

______________________________________________________________________

### method `process_args`

**Source:** [`cli.py:54`](https://github.com/robocorp/robocorp/tree/master/tasks/src/robocorp/tasks/cli.py#L54)

```python
process_args(args: List[str]) → int
```

**Args:**

- <b>`args`</b>:  The arguments to process.

Returns: the exitcode.
