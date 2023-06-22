NEXT
-----------------------------

- The execution of `while` statements is now shown in the log.
- The execution of `if/elif/else` statements is now shown in the log.

1.1.0 (2023-06-20)
-----------------------------

- If the depth of a recursion is > 20 it will be shown in the same level so
  that messages are still readable.
  
- Fixes regarding reinitializing the stack state when a file is rotated.

- If the log is partial a message is shown to the user.
  
- It's possible to specify whether the default theme to be used is `dark` 
  or `light` by passing arguments in the `log.html`. 
  
  i.e.: `log.html?theme=dark`
  
- Variable pretty-printing improvements
    - if a variable representation is considered small its contents won't be broken into new lines.

      i.e.: `(a, b, c)` will be shown as is instead of being broken into 5 lines.

    - Unbalanced tokens such as `[` or `]` without a counterpart are better handled.
  
- Improvements to the degenerate case where the chosen max log file
is too close to the size of a single message:

To improve this case, a `min_messages_per_file` was added to 
`robocorp.log.add_log_output` where it'll only start rotating to a new file after
a given amount of messages was given (the default is now `50`)
and the maximum size for a repr can be set (by default it's now set to `200k` 
chars before clipping the `repr(obj)`).

- New API: `robocorp.log.setup_log`:

```python
def setup_log(*, max_value_repr_size: Optional[Union[str, int]] = None):
    """
    Setups the log "general" settings.

    Args:
        max_value_repr_size: This is the maximum number of chars which
            may be used for a repr (values are clipped if a `repr(obj)` would
            return a bigger representation).
            May be passed directly as the value as an int or a string with the
            value and associated unit.
            Accepted units are: `k`, `m`.
            Example: `"1000k"`, `"1m"`.

            The default value for this setting is "200k".
    """
```

- New parameter in `robocorp.log.add_log_output`:

    `min_messages_per_file`: This is the minimum number of messages that need
        to be added to a file for it to be rotated (if messages are too big
        this may make the max_file_size be surpassed). This is needed to
        prevent a case where a whole new file could be created after just
        a single message if the message was too big for the max file size.


1.0.1 (2023-06-14)
-----------------------------

- Improvements in `log.html`:
    - Variables are now pretty-printed in details.
    - Variables in the tree are always shown in a single line.


1.0.0 (2023-06-13)
-----------------------------

- `for` statement: code is no longer rewritten to add two `try..except..finally` blocks for each for loop. 
- Semantic versioning now used.
- Classifier changed to `Beta`.

0.3.1
-----------------------------

- `for` loops shown in log.
- Stack visualization improved.
- Run properly marked as failed when it fails.
- Write in chunks to stdout when `RC_LOG_OUTPUT_STDOUT` is specified.

0.3.0
-----------------------------

- New API: `robocorp.log.process_snapshot()`:
    Makes a process snapshot and adds it to the logs.
    A process snapshot can include details on the python process and subprocesses
    and should add a thread dump with the stack of all running threads.

0.2.0
-----------------------------

- New features in `log.html`:
    - Redesigned (now uses react and the tree can handle much more items).
    - Filtering is now available.
    - It's possible to click elements to see details.
    - Full traceback with variables available.


0.1.1
-----------------------------

- Documentation updates

0.1.0
-----------------------------

- `log.html`: Exception message is now in the details (so it can be expanded).


0.0.15
-----------------------------

- When an exception is logged, local variablas are properly redacted for sensitive information.
- Support multiple yields appearing as expressions in one statement.
- Redirecting messages written to the console to log messages.


0.0.14
-----------------------------

- Format improvement: the location (name,libname,filename,lineno,docstring) is embedded/referenced in a single message.

0.0.13
-----------------------------

- Log: Support `yield from` statements in the auto-logging.
- Log: Fixes in support for `yield`.
    - Current yield limitation: When yield is inside another expression it won't 
      show the yielded value (i.e.: `x = call() and yield another()` won't show the `another()` value) 
      as doing so could change the order of calls.
- Log cli: Properly assign args to generator.
- Public API change: `critical`/`warn`/`info` methods now accept multiple arguments and all are
  concatenated and converted to `str`.
    - Old api: `robocorp.log.info(messsage: str, html: bool=False)`
    - New api: `robocorp.log.info(*message)`
- New API to embed html into the page:
    - `robocorp.log.html(html: str, level: str = "INFO")`
        - `level` may be `"INFO"`, `"WARN"` or `"ERROR"`

0.0.12
-----------------------------

- First alpha for early adapters.
- Basic ascii-based structured logging.
- Rotating output based on the log size and number of files to keep.
- Time available.
- Run name available.
- Auto-logging for method calls.
- Auto-logging for method arguments.
- Auto-logging for assigns.
- Auto-logging for exceptions.
- APIs to add log messages (critical, warn, info, exception).
- APIs to hide sensitive information.
- Status of the run/task/method available.
- Auto-logging for methods with `yield`.
- Auto-logging for code considered `user code` by default.
- Auto-logging can be customized to log `library code` of specific libraries.

Known limitations:
- Logging may be confused by `yield from` and `async`/`await`.
- Logging is only provided for the main thread.

Note:

- The internal format may still change. As such it's recommended that the `log.html`
  is kept as it bundles the data generated with a viewer for the generated logs to
  actually interpret the logs.