<!-- markdownlint-disable -->

# module `robocorp.log.redirect`

# Functions

______________________________________________________________________

## `setup_stdout_logging`

This function is responsible for setting up the needed stdout/stderr redirections (usually managed from robocorp-tasks).

The redirections needed are:
\- Redirect stdout and stderr to `console_messages` ifredirect_to_console_messages is True (while still printing tothe original streams).
\- Write all the messages to the stdout if the mode is "json" or ifthe mode is "" and the "RC_LOG_OUTPUT_STDOUT" is set toone of ("1", "t", "true", "json").

**Args:**

- <b>`mode`</b>:  "": query the RC_LOG_OUTPUT_STDOUT value. "no": don't provide log output to the stdout. "json": provide json output to the stdout.

- <b>`redirect_to_console_messages`</b>:  Whether messages sent to stdout and stderr should be redirected to console messages.

[**Link to source**](https://github.com/robocorp/robocorp/tree/master/log/robocorp/log/redirect/setup_stdout_logging#L136)

```python
setup_stdout_logging(
    mode: str,
    redirect_to_console_messages: bool = True
) → Iterator[NoneType]
```
