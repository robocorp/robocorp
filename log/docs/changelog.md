NEXT
-----------------------------

- Log: Support `yield from` statements in the auto-logging.
- Log cli: Properly assign args to generator.
- Public API change: `critical`/`warn`/`info` methods now accept multiple arguments and all are concatenated and converted to `str`.
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