<!-- markdownlint-disable -->

# module `robocorp.log`

**Source:** [`__init__.py:0`](https://github.com/robocorp/robocorp/tree/master/log/src/robocorp/log/__init__.py#L0)

## Variables

- **protocols**
- **version_info**

______________________________________________________________________

## function `critical`

**Source:** [`__init__.py:107`](https://github.com/robocorp/robocorp/tree/master/log/src/robocorp/log/__init__.py#L107)

```python
critical(*message: Any) → None
```

Adds a new logging message with a critical (error) level.

**Args:**

- <b>`message`</b>:  The message which should be logged.

**Example:**

```python
critical('Failed because', obj, 'is not', expected)
```

**Note:**

> Formatting converts all objects given to `str`. If you need custom formatting please pre-format the string. i.e.: `critical(f'Failed because {obj!r} is not {expected!r}.')`

**Note:**

> A new line is automatically added at the end of the message.

**Note:**

> See: `setup_log()` for configurations which may filter out the logged calls and also print it to a stream (such stdout/stderr).

______________________________________________________________________

## function `warn`

**Source:** [`__init__.py:134`](https://github.com/robocorp/robocorp/tree/master/log/src/robocorp/log/__init__.py#L134)

```python
warn(*message: Any) → None
```

Adds a new logging message with a warn level.

**Args:**

- <b>`message`</b>:  The message which should be logged.

**Example:**

```python
warn('Did not expect', obj)
```

**Note:**

> Formatting converts all objects given to `str`. If you need custom formatting please pre-format the string. i.e.: `warn(f'Did not expect {obj!r}.')`

**Note:**

> A new line is automatically added at the end of the message.

**Note:**

> See: `setup_log()` for configurations which may filter out the logged calls and also print it to a stream (such stdout/stderr).

______________________________________________________________________

## function `info`

**Source:** [`__init__.py:161`](https://github.com/robocorp/robocorp/tree/master/log/src/robocorp/log/__init__.py#L161)

```python
info(*message: Any) → None
```

Adds a new logging message with an info level.

**Args:**

- <b>`message`</b>:  The message which should be logged.

**Example:**

```python
info('Received value', obj)
```

**Note:**

> Formatting converts all objects given to `str`. If you need custom formatting please pre-format the string. i.e.: `info(f'Received value {obj!r}.')`

**Note:**

> A new line is automatically added at the end of the message.

**Note:**

> See: `setup_log()` for configurations which may filter out the logged calls and also print it to a stream (such stdout/stderr).

______________________________________________________________________

## function `debug`

**Source:** [`__init__.py:189`](https://github.com/robocorp/robocorp/tree/master/log/src/robocorp/log/__init__.py#L189)

```python
debug(*message: Any) → None
```

Adds a new logging message with an debug level.

**Args:**

- <b>`message`</b>:  The message which should be logged.

**Example:**

```python
debug('Received value', obj)
```

**Note:**

> Formatting converts all objects given to `str`. If you need custom formatting please pre-format the string. i.e.: `debug(f'Received value {obj!r}.')`

**Note:**

> A new line is automatically added at the end of the message.

**Note:**

> See: `setup_log()` for configurations which may filter out the logged calls and also print it to a stream (such stdout/stderr).

______________________________________________________________________

## function `exception`

**Source:** [`__init__.py:217`](https://github.com/robocorp/robocorp/tree/master/log/src/robocorp/log/__init__.py#L217)

```python
exception(*message: Any)
```

Adds to the logging the exceptions that's currently raised.

**Args:**

- <b>`message`</b>:  If given an additional error message to be shown.

**Note:**

> In general this method does NOT need to be called as exceptions found are automatically tracked by the framework.

**Note:**

> A new line is automatically added at the end of the message (if a message was given for logging).

______________________________________________________________________

## function `html`

**Source:** [`__init__.py:241`](https://github.com/robocorp/robocorp/tree/master/log/src/robocorp/log/__init__.py#L241)

```python
html(html: str, level: str = 'INFO')
```

Adds html contents to the log.

**Args:**

- <b>`html`</b>:  The html content to be embedded in the page.
- <b>`level`</b>:  The level of the message ("INFO", "WARN" or "ERROR")

Example adding an image:

```python
html(

 - <b>`    '<img src="data`</b>: image/png;base64,iVBORw0KGgoAAAANSUhEUgAAACwAAAAnBAMAAACGbbfxAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAbUExURR4nOzpCVI+Tnf///+Pk5qqutXN4hVZdbMbJzod39mUAAAAJcEhZcwAADsMAAA7DAcdvqGQAAAETSURBVDjLnZIxT8MwFITPqDQdG1rBGjX8AOBS0hG1ghnUhbFSBlZvMFbqH+fZaeMLBJA4KZHzyb7ce374l1we3vm0Ty/Ix7era1YvSjOeVBWCZx3mveBDwlWyH1OUXM5t0yJqS+4V33xdwWFCrvOoOfmA1r30Z+r9jHV7zmeKd7ADQEOvATkFlzGz13JqIGanYbexYLOldcY+IsniqrEyRrUj7xBwccRm/lSuPqysI3YBjzUfQproNOr/0tLEgE3CK8P2YG54K401XIeWHDw2Uo5H5UP1l1ZXr9+7U2ffRfhTC9HwFVMmqOzl7vTDnEwSvhXsNLaoGbIGurvf97ArhzYbj01sm6TKXm3yC3yX8/hdwCdipl9ujxriXgAAAABJRU5ErkJggg=="/>'
)
```

______________________________________________________________________

## function `process_snapshot`

**Source:** [`__init__.py:261`](https://github.com/robocorp/robocorp/tree/master/log/src/robocorp/log/__init__.py#L261)

```python
process_snapshot() → None
```

Makes a process snapshot and adds it to the logs.

A process snapshot can include details on the python process and subprocesses and should add a thread dump with the stack of all running threads.

______________________________________________________________________

## function `console_message`

**Source:** [`__init__.py:304`](https://github.com/robocorp/robocorp/tree/master/log/src/robocorp/log/__init__.py#L304)

```python
console_message(
    message: str,
    kind: str,
    stream: Union[IO, NoneType, _SentinelUseStdout] = <robocorp.log._SentinelUseStdout object at 0x10585afb0>,
    flush: Optional[bool] = None
) → None
```

Shows a message in the console and also adds it to the log output.

**Args:**

```
 - <b>`message`</b>:  The message to be added to the log.kind:
 - <b>`User messages (note`</b>:  the redirect feature which would add these automatically -- if that's the case, the 'stream' would need to be None so that it's not written again):
 - <b>`"stdout"`</b>:  Some user message which was being sent to the stdout.
 - <b>`"stderr"`</b>:  Some user message which was being sent to the stderr.
```

Messages from the framework:
\- <b>`"regular"`</b>:  Some regular message.
\- <b>`"important"`</b>:  Some message which deserves a bit more attention.
\- <b>`"task_name"`</b>:  The task name is being written.
\- <b>`"error"`</b>:  Some error message.
\- <b>`"traceback"`</b>:  Some traceback message.
\- <b>`stream`</b>:  If specified this is the stream where the message should also be written.
\- if not specified (\_SentinelUseStdout) it's written to sys.stdout by default.
\- if None it's not written.
\- <b>`flush`</b>:  Whether we should flush after sending the message (if None it's flushed if the end char ends with '').

______________________________________________________________________

## function `suppress_methods`

**Source:** [`__init__.py:411`](https://github.com/robocorp/robocorp/tree/master/log/src/robocorp/log/__init__.py#L411)

```python
suppress_methods()
```

Can be used as a context manager or decorator so that methods are not logged.

i.e.:

```python
@suppress_methods
def method():
    ...
```

or

```python
with suppress_methods():
    ...
```

______________________________________________________________________

## function `suppress_variables`

**Source:** [`__init__.py:432`](https://github.com/robocorp/robocorp/tree/master/log/src/robocorp/log/__init__.py#L432)

```python
suppress_variables()
```

Can be used as a context manager or decorator so that variables are not logged.

i.e.:

```python
@suppress_variables
def method():
    ...
```

or

```python
with suppress_variables():
    ...
```

______________________________________________________________________

## function `suppress`

**Source:** [`__init__.py:481`](https://github.com/robocorp/robocorp/tree/master/log/src/robocorp/log/__init__.py#L481)

```python
suppress(*args, **kwargs)
```

API to suppress logging to be used as a context manager or decorator.

By default suppresses everything and its actual API is something as:

def suppress(variables:bool = True, methods:bool = True): ...

**Args:**

- <b>`variables`</b>:  Whether variables should be suppressed in the scope.

- <b>`methods`</b>:  Whether method calls should be suppressed in the scope.

Usage as a decorator:

```python
from robocorp import log

@log.suppress
def func():
    ....
```

Usage as a decorator suppressing only variables:

```python
from robocorp import log

@log.suppress(methods=False)
def func():
    ....
```

Usage as a context manager:

```python
from robocorp import log

with log.suppress(methods=False):
    ....
```

______________________________________________________________________

## function `is_sensitive_variable_name`

**Source:** [`__init__.py:527`](https://github.com/robocorp/robocorp/tree/master/log/src/robocorp/log/__init__.py#L527)

```python
is_sensitive_variable_name(variable_name: str) → bool
```

Returns true if the given variable name should be considered sensitive.

**Args:**

- <b>`variable_name`</b>:  The variable name to be checked.

**Returns:**
True if the given variable name is considered to be sensitive (in whichcase its value should be redacted) and False otherwise.

______________________________________________________________________

## function `add_sensitive_variable_name`

**Source:** [`__init__.py:541`](https://github.com/robocorp/robocorp/tree/master/log/src/robocorp/log/__init__.py#L541)

```python
add_sensitive_variable_name(variable_name: str) → None
```

Marks a given variable name as sensitive

(in this case any variable containing the given `variable_name` will be redacted).

Note that this will add a patterns where any variable containing the given variable name even as a substring will be considered sensitive.

**Args:**

- <b>`variable_name`</b>:  The variable name to be considered sensitive.

______________________________________________________________________

## function `add_sensitive_variable_name_pattern`

**Source:** [`__init__.py:557`](https://github.com/robocorp/robocorp/tree/master/log/src/robocorp/log/__init__.py#L557)

```python
add_sensitive_variable_name_pattern(variable_name_pattern: str) → None
```

Adds a given pattern to consider a variable name as sensitive.

Any variable name matching the given pattern will have its value redacted.

**Args:**

- <b>`variable_name_pattern`</b>:  The variable name pattern to be consideredsensitive.

______________________________________________________________________

## function `hide_from_output`

**Source:** [`__init__.py:570`](https://github.com/robocorp/robocorp/tree/master/log/src/robocorp/log/__init__.py#L570)

```python
hide_from_output(string_to_hide: str) → None
```

Should be called to hide sensitive information from appearing in the output.

Note that any variable assign or argument which is set to a name containing the string:

'password' or 'passwd'

Will be automatically hidden and it's also possible to add new names to be automatically redacted withe the methods: `add_sensitive_variable_name` and `add_sensitive_variable_name_pattern`.

**Args:**

- <b>`string_to_hide`</b>:  The string that should be hidden from the output.

______________________________________________________________________

## function `hide_strings_config`

**Source:** [`__init__.py:613`](https://github.com/robocorp/robocorp/tree/master/log/src/robocorp/log/__init__.py#L613)

```python
hide_strings_config() → IRedactConfiguration
```

Can be used to configure heuristics on what should be hidden and what should not be hidden from the logs.

**Example:**

```python
from robocorp import log
config = log.hide_strings_config()

# The word 'House' will not be hidden going forward.
config.dont_hide_strings.add('House')

# By default 'True' is not hidden, change it so that it is hidden if
# requested.
config.dont_hide_strings.discard('True')

# Note: this has the same effect as `log.hide_from_output('True')`
config.hide_strings.add('True')

# It's also possible to determine the minimum size of the strings
# to be redacted. The setting below sets things so that strings
# with 1, 2 or 3 chars won't be hidden.
config.dont_hide_strings_smaller_or_equal_to = 3
```

______________________________________________________________________

## function `start_run`

**Source:** [`__init__.py:645`](https://github.com/robocorp/robocorp/tree/master/log/src/robocorp/log/__init__.py#L645)

```python
start_run(name: str) → None
```

Starts a run session (adds the related event to the log).

**Args:**

- <b>`name`</b>:  The name of the run.

Note: robocorp-tasks calls this method automatically.

______________________________________________________________________

## function `end_run`

**Source:** [`__init__.py:659`](https://github.com/robocorp/robocorp/tree/master/log/src/robocorp/log/__init__.py#L659)

```python
end_run(name: str, status: str) → None
```

Finishes a run session (adds the related event to the log).

**Args:**

- <b>`name`</b>:  The name of the run.
- <b>`status`</b>:  The run status.

Note: robocorp-tasks calls this method automatically.

______________________________________________________________________

## function `start_task`

**Source:** [`__init__.py:674`](https://github.com/robocorp/robocorp/tree/master/log/src/robocorp/log/__init__.py#L674)

```python
start_task(
    name: str,
    libname: str,
    source: str,
    lineno: int,
    doc: str = ''
) → None
```

Starts a task (adds the related event to the log).

**Args:**

- <b>`name`</b>:  The name of the task.
- <b>`libname`</b>:  The library (module name) where the task is defined.
- <b>`source`</b>:  The source of the task.
- <b>`lineno`</b>:  The line number of the task in the given source.
- <b>`doc`</b>:  The documentation for the task.

Note: robocorp-tasks calls this method automatically.

______________________________________________________________________

## function `end_task`

**Source:** [`__init__.py:694`](https://github.com/robocorp/robocorp/tree/master/log/src/robocorp/log/__init__.py#L694)

```python
end_task(name: str, libname: str, status: str, message: str) → None
```

Ends a task (adds the related event to the log).

**Args:**

- <b>`name`</b>:  The name of the task.
- <b>`libname`</b>:  The library (module name) where the task is defined.
- <b>`status`</b>:  The pass/fail status of the task
- <b>`message`</b>:  The message for a failed task

Note: robocorp-tasks calls this method automatically.

______________________________________________________________________

## function `iter_decoded_log_format_from_stream`

**Source:** [`__init__.py:714`](https://github.com/robocorp/robocorp/tree/master/log/src/robocorp/log/__init__.py#L714)

```python
iter_decoded_log_format_from_stream(stream: IReadLines) → Iterator[dict]
```

Iterates stream contents and decodes those as dicts.

**Args:**

- <b>`stream`</b>:  The stream which should be iterated in (anything with a `readlines()` method which should provide the messages encoded in the internal format).

**Returns:**
An iterator which will decode the messages and provides a dictionary foreach message found.

Example of messages provided:

```python

 - <b>`{'message_type'`</b>:  'V', 'version': '1'}

 - <b>`{'message_type'`</b>:  'T', 'time': '2022-10-31T07:45:57.116'}

 - <b>`{'message_type'`</b>:  'ID', 'part': 1, 'id': 'gen-from-output-xml'}

 - <b>`{'message_type'`</b>:  'SR', 'name': 'Robot Check', 'time_delta_in_seconds': 0.3}
...
```

- <b>`Note`</b>:  the exact format of the messages provided is not stable acrossreleases.

______________________________________________________________________

## function `iter_decoded_log_format_from_log_html`

**Source:** [`__init__.py:745`](https://github.com/robocorp/robocorp/tree/master/log/src/robocorp/log/__init__.py#L745)

```python
iter_decoded_log_format_from_log_html(log_html: Path) → Iterator[dict]
```

Reads the data saved in the log html and provides decoded messages (dicts).

**Returns:**
An iterator which will decode the messages and provides a dictionary for each message found.

Example of messages provided:

```python

 - <b>`{'message_type'`</b>:  'V', 'version': '1'}

 - <b>`{'message_type'`</b>:  'T', 'time': '2022-10-31T07:45:57.116'}

 - <b>`{'message_type'`</b>:  'ID', 'part': 1, 'id': 'gen-from-output-xml'}

 - <b>`{'message_type'`</b>:  'SR', 'name': 'Robot Check', 'time_delta_in_seconds': 0.3}
...
```

- <b>`Note`</b>:  the exact format of the messages provided is not stable acrossreleases.

______________________________________________________________________

## function `verify_log_messages_from_messages_iterator`

**Source:** [`__init__.py:805`](https://github.com/robocorp/robocorp/tree/master/log/src/robocorp/log/__init__.py#L805)

```python
verify_log_messages_from_messages_iterator(
    messages_iterator: Iterator[dict],
    expected: Sequence[dict],
    not_expected: Sequence[dict] = ({'message_type': 'L', 'level': 'E'},)
) → List[dict]
```

Helper for checking that the expected messages are found in the given messages iterator.

Can also check if a message is not found.

**Args:**

- <b>`messages_iterator`</b>:  An iterator over the messages found.
- <b>`expected`</b>:  The messages which are expected to be found. If some message expected to be found is not found an AssertionError will be raised.
- <b>`not_expected`</b>:  The messages that should not appear.

**Example:**

```python
verify_log_messages_from_messages_iterator(
messages_iterator,
[
    {'message_type': 'V', 'version': '1'}
    {'message_type': 'T', 'time': '2022-10-31T07:45:57.116'}
]
```

Note: if one of the key entries is `__check__` the value will be considered a callable which should return `True` or `False` to determine if a match was made.

**Example:**

```python
verify_log_messages_from_messages_iterator(
messages_iterator,
[
    {
        "message_type": "T",
        # i.e.: check for the utc timezone (+00:00) in the time.
        "__check__": lambda msg: msg["time"].endswith("+00:00"),
    },
]
```

______________________________________________________________________

## function `verify_log_messages_from_decoded_str`

**Source:** [`__init__.py:886`](https://github.com/robocorp/robocorp/tree/master/log/src/robocorp/log/__init__.py#L886)

```python
verify_log_messages_from_decoded_str(
    s: str,
    expected: Sequence[dict],
    not_expected: Sequence[dict] = ({'message_type': 'L', 'level': 'E'},)
) → List[dict]
```

Verifies whether the given messages are available or not in the decoded messages.

**Args:**

- <b>`s`</b>:  A string with the messages already decoded (where messages areseparated by lines and each message is a json string to be decoded).
- <b>`expected`</b>:  The messages expected.
- <b>`not_expected`</b>:  The messages that should not appear.

See: `verify_log_messages_from_messages_iterator` for more details on the matching of messages.

______________________________________________________________________

## function `verify_log_messages_from_log_html`

**Source:** [`__init__.py:944`](https://github.com/robocorp/robocorp/tree/master/log/src/robocorp/log/__init__.py#L944)

```python
verify_log_messages_from_log_html(
    log_html: Path,
    expected: Sequence[dict],
    not_expected: Sequence[dict] = ({'message_type': 'L', 'level': 'E'},)
) → List[dict]
```

Verifies whether the given messages are available or not in the decoded messages.

**Args:**

- <b>`log_html`</b>:  The path to the log_html where messages were embedded.
- <b>`expected`</b>:  The messages expected.
- <b>`not_expected`</b>:  The messages that should not appear.

See: `verify_log_messages_from_messages_iterator` for more details on the matching of messages.

______________________________________________________________________

## function `verify_log_messages_from_stream`

**Source:** [`__init__.py:964`](https://github.com/robocorp/robocorp/tree/master/log/src/robocorp/log/__init__.py#L964)

```python
verify_log_messages_from_stream(
    stream: IReadLines,
    expected: Sequence[dict],
    not_expected: Sequence[dict] = ({'message_type': 'L', 'level': 'E'},)
) → Sequence[dict]
```

Verifies whether the given messages are available or not in the decoded messages.

**Args:**

- <b>`stream`</b>:  A stream from where the encoded messages are expected to be read from.
- <b>`expected`</b>:  The messages expected.
- <b>`not_expected`</b>:  The messages that should not appear.

See: `verify_log_messages_from_messages_iterator` for more details on the matching of messages.

______________________________________________________________________

## function `setup_log`

**Source:** [`__init__.py:1020`](https://github.com/robocorp/robocorp/tree/master/log/src/robocorp/log/__init__.py#L1020)

```python
setup_log(
    max_value_repr_size: Optional[str, int] = None,
    log_level: Optional[FilterLogLevel, Literal['debug', 'warn', 'info', 'critical', 'none']] = None,
    output_log_level: Optional[FilterLogLevel, Literal['debug', 'warn', 'info', 'critical', 'none']] = None,
    output_stream: Optional[Literal['stdout', 'stderr'], Dict[Union[FilterLogLevel, Literal['debug', 'warn', 'info', 'critical', 'none']], Literal['stdout', 'stderr']]] = None
) → IContextManager
```

Setups the log "general" settings.

**Args:**

- <b>`max_value_repr_size`</b>:  This is the maximum number of chars which may be used for a repr (values are clipped if a `repr(obj)` would return a bigger representation). May be passed directly as the value as an int or a string with the value and associated unit.
- <b>`Accepted units are`</b>:  `k`, `m`.
- <b>`Example`</b>:  `"1000k"`, `"1m"`.

The default value for this setting is "200k".

- <b>`log_level`</b>:  Messages with a level higher or equal to the one specified will be logged in the `log.html`.

The default value for this setting is "FilterLogLevel.DEBUG", so, any message logged with `log.debug`, `log.info`, `log.warn` and `log.critical` will be shown.

- <b>`output_log_level`</b>:  Messages with a level higher or equal to the one specified will be printed to the output_stream configured.

The default value for this setting is "FilterLogLevel.NONE", so, any message logged with `log.debug`, `log.info`, `log.warn` and `log.critical` is not shown in the output.

- <b>`output_stream`</b>:  It's possible to specify the stream to output contents to be printed in the `log.debug`, `log.info`, `log.warn` and `log.critical` calls. If all messages should be streamed to the same place it can be the output stream (or its name) or it can be a dict mapping each level to a different stream (or its name).
- <b>`Note`</b>:  if sys.stdout/sys.stderr are used it's preferred to pass it asa literal (`"stdout"` or `"stderr"`) as if the stream is redirected it'llstill print to the current `sys.stdout` / `sys.stderr`.

**Returns:**
A context manager, so, it's possible to use this method with a `with statement`so that the configuration is reverted to a previous configuration whenthe context manager exits (if not called with a `with statement` thenthe values won't be reverted).

**Example:**

Setting the max repr size:

```python
from robocorp import log
# If a repr(obj) returns a string bigger than 100000 chars it'll
# be clipped to 100000 chars.
log.setup_log(max_value_repr_size=100_000)
```

**Example:**

Configuring to log only `log.critical`:

```python
from robocorp import log
log.setup_log(log_level=log.FilterLogLevel.CRITICAL)
```

**Example:**

Configuring to print log.warn messages to sys.stdout and log.criticalmessages to sys.stderr:

```python
from robocorp import log
log.setup_log(
    output_log_level='warn',
    output_stream={'warn': 'stdout', 'critical': 'stderr'}
)
```

______________________________________________________________________

## function `setup_auto_logging`

**Source:** [`__init__.py:1154`](https://github.com/robocorp/robocorp/tree/master/log/src/robocorp/log/__init__.py#L1154)

```python
setup_auto_logging(
    config: Optional[AutoLogConfigBase] = None,
    add_rewrite_hook: bool = True
)
```

Sets up automatic logging.

This must be called prior to actually importing the modules which should be automatically logged.

**Args:**

- <b>`config`</b>:  The configuration specifying how modules should be automatically logged.

If not passed, by default all files which are library files (i.e.: in the python `Lib` or `site-packages`) won't be logged and all files which are not library files will be fully logged.

Returns a context manager which will stop applying the auto-logging to new loaded modules. Note that modules which are already being tracked won't stop being tracked.

______________________________________________________________________

## function `add_log_output`

**Source:** [`__init__.py:1187`](https://github.com/robocorp/robocorp/tree/master/log/src/robocorp/log/__init__.py#L1187)

```python
add_log_output(
    output_dir: Union[str, Path],
    max_file_size: str = '1MB',
    max_files: int = 5,
    log_html: Optional[str, Path] = None,
    log_html_style: Literal['standalone', 'vscode'] = 'standalone',
    min_messages_per_file: int = 50
)
```

Adds a log output which will write the contents to the given output directory.

Optionally it's possible to collect all the output when the run is finished and put it into a log.html file.

**Args:**

- <b>`output_dir`</b>:  The output directory where the log contents should be saved.
- <b>`max_file_size`</b>:  The maximum file size for one log file (as a string with
- <b>`the value and the unit -- accepted units are`</b>:  `b`, `kb`, `mb`, `gb`if no unit is passed it's considered `b` (bytes)).Note that the max size is not a hard guarantee, rather it's aguideline that the logging tries to follow (usually it's very close,although on degenerate cases it can be considerably different).
- <b>`max_files`</b>:  The maximum amount of files which can be added (if more would be needed the oldest one is erased).
- <b>`log_html`</b>:  If given this is the path (file) where the log.html contents should be written (the log.html will include all the logs from the run along with a viewer for such logs).
- <b>`log_html_style`</b>:  The style to be used for the log.html.
- <b>`min_messages_per_file`</b>:  This is the minimum number of messages that need to be added to a file for it to be rotated (if messages are too big this may make the max_file_size be surpassed). This is needed to prevent a case where a whole new file could be created after just a single message if the message was too big for the max file size.

**Note:**

> It's Ok to add more than one log output, but if 2 log outputs point to the same directory there will be conflicts (in the future this should generate an error).

______________________________________________________________________

## function `close_log_outputs`

**Source:** [`__init__.py:1251`](https://github.com/robocorp/robocorp/tree/master/log/src/robocorp/log/__init__.py#L1251)

```python
close_log_outputs()
```

This method must be called to close loggers.

Note that some loggers such as the one which outputs html needs to bo closed to actually write the output.

______________________________________________________________________

## function `add_in_memory_log_output`

**Source:** [`__init__.py:1268`](https://github.com/robocorp/robocorp/tree/master/log/src/robocorp/log/__init__.py#L1268)

```python
add_in_memory_log_output(write: Callable[[str], Any])
```

Adds a log output which is in-memory (receives a callable).

**Args:**

- <b>`write`</b>:  A callable which will be called as `write(msg)` whenevera message is sent from the logging.

**Returns:**
A context manager which can be used to automatically remove andclose the related logger.

______________________________________________________________________

## class `ConsoleMessageKind`

**Source:** [`__init__.py:273`](https://github.com/robocorp/robocorp/tree/master/log/src/robocorp/log/__init__.py#L273)

______________________________________________________________________

## class `IRedactConfiguration`

**Source:** [`__init__.py:590`](https://github.com/robocorp/robocorp/tree/master/log/src/robocorp/log/__init__.py#L590)

#### property `dont_hide_strings`

This provides the set of strings that should not be hidden from the logs.

The default strings that should not be hidden are: 'None', 'True', 'False'

#### property `hide_strings`

This provides the set of strings that should be hidden from the logs.

______________________________________________________________________

## enum `FilterLogLevel`

**Source:** [`__init__.py:989`](https://github.com/robocorp/robocorp/tree/master/log/src/robocorp/log/__init__.py#L989)

An enumeration.

### Values

- **DEBUG** = debug
- **WARN** = warn
- **INFO** = info
- **CRITICAL** = critical
- **NONE** = none

______________________________________________________________________

## class `IContextManager`

**Source:** [`__init__.py:1000`](https://github.com/robocorp/robocorp/tree/master/log/src/robocorp/log/__init__.py#L1000)

Typing for a "generic" context manager.
