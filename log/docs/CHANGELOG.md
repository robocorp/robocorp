# Changelog

## Unreleased

## 3.0.1 - 2025-06-23

- Updating dependencies

## 3.0.0 - 2025-04-22

- Fix issue where the `<img>` contents were being redacted (now, if `html` is `True` in `robocorp.log.info` the contents of `<img>` tags are not redacted).
- The string printed to the output is now `Log (html): <path-to-log-file>` instead of `Robocorp Log (html): <path-to-log-file>`.

## 2.9.6 - 2025-02-25

- Update dependencies

## 2.9.3 - 2024-09-25

- Update dependencies

## 2.9.2 - 2024-04-08

- Update package's main README.

## 2.9.1 - 2024-03-11

- Fixed issue writing unicode to the output when the contents cannot be encoded with the stdout/stderr encoding.

## 2.9.0 - 2024-01-19

- Added auxiliary function `iter_decoded_log_format_from_log_html_contents` to `robocorp.log` to public API.

## 2.8.1 - 2024-01-14

- Fix main README and update docs.
- Fix version retrieval during development.

## 2.8.0 - 2023-10-27

- `log.html`: It's now possible to click icon to show details (so, items without a message are also clickable).
- `log.html`: The copy to clipboard button for variables no longer hides variable content.
- If greenlet is available, also check if the current greenlet matches for logging (as logging from different greenlet threads messes up the stack).
- Don't hide from the logs common python words: `None`, `True`, `False` as well as strings with 2 or less characters.
- New API to specify which words should not be hidden (`robocorp.log.hide_strings_config()`).

## 2.7.1 - 2023-09-07

- A case where the stack could become inconsistent when using yield was fixed.
- Performance improvements (it's now 20% faster to import modules).

## 2.7.0 - 2023-08-21

- `if` statements now create a scope in `log.html` (when the function is not a generator).
- If an exception has a cause or context the context/cause is now shown in the log
  - (i.e.: when an exception is raised from another exception or is raised while handling another exception all exceptions are shown).
- `continue` and `break` inside a loop are properly handled.
- `continue` and `break` are now shown in the logs.
- It's now possible to expand / collapse recursively in `log.html`.
- `log.html`: When navigating using left arrow, if the element is already collapsed the parent is focused.
- Spec version changed from `0.0.3` to `0.0.4`.
- `re.Pattern` is now accepted at `add_sensitive_variable_name_pattern`.

## 2.6.0 - 2023-08-04

- `log.html`:

  - Tree usability improvements:
    - When an item is expanded its children are scrolled into the tree.
    - When row is focused, `Enter` can be used to open item details and `Space` to expand and collapse.
    - When expand button is focused both `Enter` and `Space' can be used to expand and collapse.
    - Clicking on row will show row focused.
    - Clicking on row title will open item details.

- Improved UI when logs are rotated out.
- `log.html`: items are scrolled into the view when parent item is expanded.

## 2.5.0 - 2023-07-24

- Spec version changed from `0.0.2` to `0.0.3`.
- `assert` statements are now rewritten so that on failures more information is provided.

## 2.4.0 - 2023-07-19

- New APIs which allow loading `pyproject.toml` files to configure the auto log
  configuration:
  - `robocorp.log.pyproject_config.PyProjectInfo`
  - `robocorp.log.pyproject_config.read_pyproject_toml`
  - `robocorp.log.pyproject_config.read_section_from_toml`
  - `robocorp.log.pyproject_config.read_robocorp_auto_log_config`

## 2.3.0 - 2023-07-10

- Added `robocorp.log.debug` to have one more level when logging.

- It's possible to filter log levels by using `robocorp.log.setup_log`.

  i.e.: `setup_log(log_level='warn')` will only show **warn** and **critical**
  entries in the log (**info** and **debug** won't be added to the logs).

- It's possible to also redirect to `sys.stdout` and `sys.stderr` the messages
  added with **log.debug**, **log.info**, **log.warn** and **log.critical**.

  **Note**: the default is only redirecting `log.critical` calls to `stderr`.
  To redirect all, it's possible to customize the `output_log_level`.
  i.e.: `setup_log(output_log_level='debug')`.

  **Note**: it's possible to customize for each log level to which stream it's
  redirected with `setup_log(output_stream={'debug': 'stderr'})`. By default
  **warn** and **critical** go to **stderr** and **debug** and **info** go to **stdout**.

- In the `log.html`, it's possible to view log messages along with the terminal
  output.

- Inside of VSCode, places showing the file/line of messages are now clickable and
  can be used to open the file location inside of VSCode.

- Fixed issue where some lines wouldn't map to the proper location in the file.

- If the log format is newer than the one expected by the log.html the UI will show a message.

## 2.2.0 - 2023-07-06

- Initial `VSCode` integration for `log.html`:
  - A `compact` layout is now available (default on VSCode).
  - Select for different runs available when inside of VSCode.
  - Default theme based on VSCode theme.

## 2.1.0 - 2023-06-30

- `log.html`: Show user messages written to stdout and stderr in the main tree.
- `log.html`: Show general information (right now info on Python) (new button in UI).
- `log.html`: Show console messages separately (new button in UI).
- `log.html`: Improved how variables are shown in exception tracebacks.

## 2.0.0 - 2023-06-28

- Fixed handling `return` statement: when `log_on_project_call` matches for a module it'll only
  show the return value if the function was called from user code.

- Filters passed for the auto-logging now accept fnmatch-style names (i.e.: `Filter("*pydev*", kind="exclude")`
  or `Filter("*", kind="exclude")`).

Backward incompatible changes:

- Log API changed: `robocorp.log.BaseConfig` was renamed to `robocorp.log.AutoLogConfigBase`.
- Log API changed: `robocorp.log.ConfigFilesFiltering` was renamed to `robocorp.log.DefaultAutoLogConfig`.
- The log configuration now has a setting specifying the default filter kind for modules not listed which is now `log_on_project_call`.
  Note that previously it excluded from the logs anything that wasn't user code that didn't
  match a filter, now it should log those when directly called from user code.

## 1.2.0 - 2023-06-23

- The execution of `while` statements is now shown in the log.
- The execution of `if/elif/else` statements is now shown in the log.
- The execution of `return` statements is now shown in the log.
- Variables are not shown in tracebacks if variables are being suppressed.

## 1.1.0 - 2023-06-20

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

## 1.0.1 - 2023-06-14

- Improvements in `log.html`:
  - Variables are now pretty-printed in details.
  - Variables in the tree are always shown in a single line.

## 1.0.0 - 2023-06-13

- `for` statement: code is no longer rewritten to add two `try..except..finally` blocks for each for loop.
- Semantic versioning now used.
- Classifier changed to `Beta`.

## 0.3.1

- `for` loops shown in log.
- Stack visualization improved.
- Run properly marked as failed when it fails.
- Write in chunks to stdout when `RC_LOG_OUTPUT_STDOUT` is specified.

## 0.3.0

- New API: `robocorp.log.process_snapshot()`:
  Makes a process snapshot and adds it to the logs.
  A process snapshot can include details on the python process and subprocesses
  and should add a thread dump with the stack of all running threads.

## 0.2.0

- New features in `log.html`:
  - Redesigned (now uses react and the tree can handle much more items).
  - Filtering is now available.
  - It's possible to click elements to see details.
  - Full traceback with variables available.

## 0.1.1

- Documentation updates

## 0.1.0

- `log.html`: Exception message is now in the details (so it can be expanded).

## 0.0.15

- When an exception is logged, local variablas are properly redacted for sensitive information.
- Support multiple yields appearing as expressions in one statement.
- Redirecting messages written to the console to log messages.

## 0.0.14

- Format improvement: the location (name,libname,filename,lineno,docstring) is embedded/referenced in a single message.

## 0.0.13

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

## 0.0.12

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

### Known limitations

- Logging may be confused by `yield from` and `async`/`await`.
- Logging is only provided for the main thread.

### Notes

- The internal format may still change. As such it's recommended that the `log.html`
  is kept as it bundles the data generated with a viewer for the generated logs to
  actually interpret the logs.
