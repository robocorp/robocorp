<!-- markdownlint-disable -->

# module `robocorp.log.redirect`

**Source:** [`redirect.py:0`](https://github.com/robocorp/robocorp/tree/master/log/src/robocorp/log/redirect.py#L0)

______________________________________________________________________

## function `setup_stdout_logging`

**Source:** [`setup_stdout_logging:136`](https://github.com/robocorp/robocorp/tree/master/log/robocorp/log/redirect/setup_stdout_logging#L136)

```python
setup_stdout_logging(
    mode: str,
    redirect_to_console_messages: bool = True
) → Iterator[NoneType]
```

This function is responsible for setting up the needed stdout/stderr redirections (usually managed from robocorp-tasks).

The redirections needed are:
\- Redirect stdout and stderr to `console_messages` ifredirect_to_console_messages is True (while still printing tothe original streams).
\- Write all the messages to the stdout if the mode is "json" or ifthe mode is "" and the "RC_LOG_OUTPUT_STDOUT" is set toone of ("1", "t", "true", "json").

**Args:**
mode:

- <b>`""`</b>:  query the RC_LOG_OUTPUT_STDOUT value.
- <b>`"no"`</b>:  don't provide log output to the stdout.
- <b>`"json"`</b>:  provide json output to the stdout.

redirect_to_console_messages:Whether messages sent to stdout and stderr should beredirected to console messages.
