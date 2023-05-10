<!-- markdownlint-disable -->

<a href="..\..\log\src\robocorp\log\__init__.py#L0"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square" /></a>

# <kbd>module</kbd> `robocorp.log`




**Global Variables**
---------------
- **protocols**
- **version_info**

---

<a href="..\..\log\src\robocorp\log\__init__.py#L69"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square" /></a>

## <kbd>function</kbd> `critical`

```python
critical(*message: Any) → None
```

Adds a new logging message with a critical (error) level. 



**Args:**
 
 - <b>`message`</b>:  The message which should be logged. 
 - <b>`html`</b>:  If True the message passed should be rendered as HTML. 



**Example:**
 critical('Failed because', obj, 'is not', expected) 



**Note:**

> Formatting converts all objects given to `str`. If you need custom formatting please pre-format the string. i.e.: critical(f'Failed because {obj!r} is not {expected!r}.') 


---

<a href="..\..\log\src\robocorp\log\__init__.py#L89"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square" /></a>

## <kbd>function</kbd> `warn`

```python
warn(*message: Any) → None
```

Adds a new logging message with a warn level. 



**Args:**
 
 - <b>`message`</b>:  The message which should be logged. 
 - <b>`html`</b>:  If True the message passed should be rendered as HTML. 



**Example:**
 warn('Did not expect', obj) 



**Note:**

> Formatting converts all objects given to `str`. If you need custom formatting please pre-format the string. i.e.: warn(f'Did not expect {obj!r}.') 


---

<a href="..\..\log\src\robocorp\log\__init__.py#L109"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square" /></a>

## <kbd>function</kbd> `info`

```python
info(*message: Any) → None
```

Adds a new logging message with an info level. 



**Args:**
 
 - <b>`message`</b>:  The message which should be logged. 
 - <b>`html`</b>:  If True the message passed should be rendered as HTML. 





**Example:**
 info('Received value', obj) 



**Note:**

> Formatting converts all objects given to `str`. If you need custom formatting please pre-format the string. i.e.: info(f'Received value {obj!r}.') 


---

<a href="..\..\log\src\robocorp\log\__init__.py#L131"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square" /></a>

## <kbd>function</kbd> `exception`

```python
exception(*message: Any)
```

Adds to the logging the exceptions that's currently raised. 



**Args:**
 
 - <b>`message`</b>:  If given an additional error message to be shown. 
 - <b>`html`</b>:  If True the message passed should be rendered as HTML. 


---

<a href="..\..\log\src\robocorp\log\__init__.py#L147"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square" /></a>

## <kbd>function</kbd> `html`

```python
html(html: str, level: str = 'INFO')
```

Adds html contents to the log. 



**Args:**
 
 - <b>`html`</b>:  The html content to be embedded in the page. 
 - <b>`level`</b>:  The level of the message ("INFO", "WARN" or "ERROR") 

Example adding an image: 

html( 
 - <b>`'<img src="data`</b>: image/png;base64,iVBORw0KGgoAAAANSUhEUgAAACwAAAAnBAMAAACGbbfxAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAbUExURR4nOzpCVI+Tnf///+Pk5qqutXN4hVZdbMbJzod39mUAAAAJcEhZcwAADsMAAA7DAcdvqGQAAAETSURBVDjLnZIxT8MwFITPqDQdG1rBGjX8AOBS0hG1ghnUhbFSBlZvMFbqH+fZaeMLBJA4KZHzyb7ce374l1we3vm0Ty/Ix7era1YvSjOeVBWCZx3mveBDwlWyH1OUXM5t0yJqS+4V33xdwWFCrvOoOfmA1r30Z+r9jHV7zmeKd7ADQEOvATkFlzGz13JqIGanYbexYLOldcY+IsniqrEyRrUj7xBwccRm/lSuPqysI3YBjzUfQproNOr/0tLEgE3CK8P2YG54K401XIeWHDw2Uo5H5UP1l1ZXr9+7U2ffRfhTC9HwFVMmqOzl7vTDnEwSvhXsNLaoGbIGurvf97ArhzYbj01sm6TKXm3yC3yX8/hdwCdipl9ujxriXgAAAABJRU5ErkJggg=="/>' ) 


---

<a href="..\..\log\src\robocorp\log\__init__.py#L197"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square" /></a>

## <kbd>function</kbd> `console_message`

```python
console_message(
    message: str,
    kind: str,
    stream: Union[IO, NoneType, _SentinelUseStdout] = <robocorp.log._SentinelUseStdout object at 0x000001C1930CE6B0>,
    flush: Optional[bool] = None
) → None
```

 Shows a message in the console and also adds it to the log output. 



**Args:**
 
     - <b>`message`</b>:  The message to be added to the log. kind: 
     - <b>`User messages (note`</b>:  the redirect feature which would add these  automatically -- if that's the case, the 'stream' would need  to be None so that it's not written again): 
     - <b>`"stdout"`</b>:  Some user message which was being sent to the stdout. 
     - <b>`"stderr"`</b>:  Some user message which was being sent to the stderr. 

Messages from the framework: 
     - <b>`"regular"`</b>:  Some regular message. 
     - <b>`"important"`</b>:  Some message which deserves a bit more attention. 
     - <b>`"task_name"`</b>:  The task name is being written. 
     - <b>`"error"`</b>:  Some error message. 
     - <b>`"traceback"`</b>:  Some traceback message. 
     - <b>`stream`</b>:  If specified this is the stream where the message should  also be written. 
            - if not specified (_SentinelUseStdout) it's written to sys.stdout by default. 
            - if None it's not written. 
     - <b>`flush`</b>:  Whether we should flush after sending the message (if None  it's flushed if the end char ends with ' '). 




---

<a href="..\..\log\src\robocorp\log\__init__.py#L302"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square" /></a>

## <kbd>function</kbd> `suppress_methods`

```python
suppress_methods()
```

Can be used as a context manager or decorator so that methods are not logged. 

i.e.:  @suppress_methods  def method():  ... 

 or 

 with suppress_methods():  ... 


---

<a href="..\..\log\src\robocorp\log\__init__.py#L319"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square" /></a>

## <kbd>function</kbd> `suppress_variables`

```python
suppress_variables()
```

Can be used as a context manager or decorator so that variables are not logged. 

i.e.:  @suppress_variables  def method():  ... 

 or 

 with suppress_variables():  ... 


---

<a href="..\..\log\src\robocorp\log\__init__.py#L364"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square" /></a>

## <kbd>function</kbd> `suppress`

```python
suppress(*args, **kwargs)
```

API to suppress logging to be used as a context manager or decorator. 

By default suppresses everything and its actual API is something as: 

def suppress(variables:bool = True, methods:bool = True):  ... 



**Args:**
 
 - <b>`variables`</b>:  Whether variables should be suppressed in the scope. 


 - <b>`methods`</b>:  Whether method calls should be suppressed in the scope. 

Usage as a decorator: 

from robocorp import log 

@log.suppress def func():  .... 

Usage as a decorator suppressing only variables: 

from robocorp import log 

@log.suppress(methods=False) def func():  .... 

Usage as a context manager: 

from robocorp import log 

with log.suppress(methods=False):  .... 


---

<a href="..\..\log\src\robocorp\log\__init__.py#L411"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square" /></a>

## <kbd>function</kbd> `is_sensitive_variable_name`

```python
is_sensitive_variable_name(variable_name: str) → bool
```

Returns true if the given variable name should be considered sensitive. 



**Args:**
 
 - <b>`variable_name`</b>:  The variable name to be checked. 



**Returns:**
 True if the given variable name is considered to be sensitive (in which case its value should be redacted) and False otherwise. 


---

<a href="..\..\log\src\robocorp\log\__init__.py#L425"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square" /></a>

## <kbd>function</kbd> `add_sensitive_variable_name`

```python
add_sensitive_variable_name(variable_name: str) → None
```

Marks a given variable name as sensitive 

(in this case any variable containing the given `variable_name` will be redacted). 

Note that this will add a patterns where any variable containing the given variable name even as a substring will be considered sensitive. 



**Args:**
 
 - <b>`variable_name`</b>:  The variable name to be considered sensitive. 


---

<a href="..\..\log\src\robocorp\log\__init__.py#L441"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square" /></a>

## <kbd>function</kbd> `add_sensitive_variable_name_pattern`

```python
add_sensitive_variable_name_pattern(variable_name_pattern: str) → None
```

Adds a given pattern to consider a variable name as sensitive. 

Any variable name matching the given pattern will have its value redacted. 



**Args:**
 
 - <b>`variable_name_pattern`</b>:  The variable name pattern to be considered sensitive. 


---

<a href="..\..\log\src\robocorp\log\__init__.py#L454"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square" /></a>

## <kbd>function</kbd> `hide_from_output`

```python
hide_from_output(string_to_hide: str) → None
```

Should be called to hide sensitive information from appearing in the output. 

Note that any variable assign or argument which is set to a name containing the string: 

'password' or 'passwd' 

Will be automatically hidden and it's also possible to add new names to be automatically redacted withe the methods: `add_sensitive_variable_name` and `add_sensitive_variable_name_pattern`. 



**Args:**
 
 - <b>`string_to_hide`</b>:  The string that should be hidden from the output. 


---

<a href="..\..\log\src\robocorp\log\__init__.py#L477"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square" /></a>

## <kbd>function</kbd> `start_run`

```python
start_run(name: str) → None
```

Starts a run session (adds the related event to the log). 



**Args:**
 
 - <b>`name`</b>:  The name of the run. 

Note: robocorp-tasks calls this method automatically. 


---

<a href="..\..\log\src\robocorp\log\__init__.py#L490"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square" /></a>

## <kbd>function</kbd> `end_run`

```python
end_run(name: str, status: str) → None
```

Finishes a run session (adds the related event to the log). 



**Args:**
 
 - <b>`name`</b>:  The name of the run. 
 - <b>`status`</b>:  The run status. 

Note: robocorp-tasks calls this method automatically. 


---

<a href="..\..\log\src\robocorp\log\__init__.py#L504"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square" /></a>

## <kbd>function</kbd> `start_task`

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


---

<a href="..\..\log\src\robocorp\log\__init__.py#L523"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square" /></a>

## <kbd>function</kbd> `end_task`

```python
end_task(name: str, libname: str, status: str, message: str) → None
```

Ends a task (adds the related event to the log). 



**Args:**
 
 - <b>`name`</b>:  The name of the task. 
 - <b>`libname`</b>:  The library (module name) where the task is defined. 
 - <b>`status`</b>:  The source of the task. 
 - <b>`message`</b>:  The line number of the task in the given source. 

Note: robocorp-tasks calls this method automatically. 


---

<a href="..\..\log\src\robocorp\log\__init__.py#L542"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square" /></a>

## <kbd>function</kbd> `iter_decoded_log_format_from_stream`

```python
iter_decoded_log_format_from_stream(stream: IReadLines) → Iterator[dict]
```

Iterates stream contents and decodes those as dicts. 



**Args:**
 
 - <b>`stream`</b>:  The stream which should be iterated in (anything with a  `readlines()` method which should provide the messages encoded  in the internal format). 



**Returns:**
 An iterator which will decode the messages and provides a dictionary for each message found. 

Example of messages provided: 


 - <b>`{'message_type'`</b>:  'V', 'version': '1'} 
 - <b>`{'message_type'`</b>:  'T', 'time': '2022-10-31T07:45:57.116'} 
 - <b>`{'message_type'`</b>:  'ID', 'part': 1, 'id': 'gen-from-output-xml'} 
 - <b>`{'message_type'`</b>:  'SR', 'name': 'Robot Check', 'time_delta_in_seconds': 0.3} ... 


 - <b>`Note`</b>:  the exact format of the messages provided is not stable across releases. 


---

<a href="..\..\log\src\robocorp\log\__init__.py#L571"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square" /></a>

## <kbd>function</kbd> `iter_decoded_log_format_from_log_html`

```python
iter_decoded_log_format_from_log_html(log_html: Path) → Iterator[dict]
```

Reads the data saved in the log html and provides decoded messages (dicts). 



**Returns:**
  An iterator which will decode the messages and provides a dictionary for  each message found. 

 Example of messages provided: 


 - <b>`{'message_type'`</b>:  'V', 'version': '1'} 
 - <b>`{'message_type'`</b>:  'T', 'time': '2022-10-31T07:45:57.116'} 
 - <b>`{'message_type'`</b>:  'ID', 'part': 1, 'id': 'gen-from-output-xml'} 
 - <b>`{'message_type'`</b>:  'SR', 'name': 'Robot Check', 'time_delta_in_seconds': 0.3} ... 


 - <b>`Note`</b>:  the exact format of the messages provided is not stable across releases. 


---

<a href="..\..\log\src\robocorp\log\__init__.py#L627"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square" /></a>

## <kbd>function</kbd> `verify_log_messages_from_messages_iterator`

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
 - <b>`expected`</b>:  The messages which are expected to be found. If some message  expected to be found is not found an AssertionError will be raised. 
 - <b>`not_expected`</b>:  The messages that should not appear. 



**Example:**
 verify_log_messages_from_messages_iterator( messages_iterator, [  {'message_type': 'V', 'version': '1'}  {'message_type': 'T', 'time': '2022-10-31T07:45:57.116'} ] 

Note: if one of the key entries is `__check__` the value will be considered a callable which should return `True` or `False` to determine if a match was made. 



**Example:**
 verify_log_messages_from_messages_iterator( messages_iterator, [  {  "message_type": "T",  # i.e.: check for the utc timezone (+00:00) in the time.  "__check__": lambda msg: msg["time"].endswith("+00:00"),  }, ] 


---

<a href="..\..\log\src\robocorp\log\__init__.py#L704"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square" /></a>

## <kbd>function</kbd> `verify_log_messages_from_decoded_str`

```python
verify_log_messages_from_decoded_str(
    s: str,
    expected: Sequence[dict],
    not_expected: Sequence[dict] = ({'message_type': 'L', 'level': 'E'},)
) → List[dict]
```

Verifies whether the given messages are available or not in the decoded messages. 



**Args:**
 
 - <b>`s`</b>:  A string with the messages already decoded (where messages are separated by lines and each message is a json string to be decoded). 
 - <b>`expected`</b>:  The messages expected. 
 - <b>`not_expected`</b>:  The messages that should not appear. 

See: `verify_log_messages_from_messages_iterator` for more details on the matching of messages. 


---

<a href="..\..\log\src\robocorp\log\__init__.py#L757"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square" /></a>

## <kbd>function</kbd> `verify_log_messages_from_log_html`

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


---

<a href="..\..\log\src\robocorp\log\__init__.py#L777"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square" /></a>

## <kbd>function</kbd> `verify_log_messages_from_stream`

```python
verify_log_messages_from_stream(
    stream: IReadLines,
    expected: Sequence[dict],
    not_expected: Sequence[dict] = ({'message_type': 'L', 'level': 'E'},)
) → Sequence[dict]
```

Verifies whether the given messages are available or not in the decoded messages. 



**Args:**
 
 - <b>`stream`</b>:  A stream from where the encoded messages are expected to be read  from. 
 - <b>`expected`</b>:  The messages expected. 
 - <b>`not_expected`</b>:  The messages that should not appear. 

See: `verify_log_messages_from_messages_iterator` for more details on the matching of messages. 


---

<a href="..\..\log\src\robocorp\log\__init__.py#L802"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square" /></a>

## <kbd>function</kbd> `setup_auto_logging`

```python
setup_auto_logging(config: Optional[BaseConfig] = None)
```

Sets up automatic logging. 

This must be called prior to actually importing the modules which should be automatically logged. 



**Args:**
 
 - <b>`config`</b>:  The configuration specifying how modules should be automatically  logged. 

 If not passed, by default all files which are library files (i.e.:  in the python `Lib` or `site-packages`) won't be logged and all files  which are not library files will be fully logged. 

Returns a context manager which will stop applying the auto-logging to new loaded modules. Note that modules which are already being tracked won't stop being tracked. 


---

<a href="..\..\log\src\robocorp\log\__init__.py#L833"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square" /></a>

## <kbd>function</kbd> `add_log_output`

```python
add_log_output(
    output_dir: Union[str, Path],
    max_file_size: str = '1MB',
    max_files: int = 5,
    log_html: Optional[str, Path] = None,
    log_html_style: Literal['standalone', 'vscode'] = 'standalone'
)
```

Adds a log output which will write the contents to the given output directory. 

Optionally it's possible to collect all the output when the run is finished and put it into a log.html file. 



**Args:**
 
 - <b>`output_dir`</b>:  The output directory where the log contents should be saved. 
 - <b>`max_file_size`</b>:  The maximum file size for one log file. 
 - <b>`max_files`</b>:  The maximum amount of files which can be added (if more would  be needed the oldest one is erased). 
 - <b>`log_html`</b>:  If given this is the path (file) where the log.html contents  should be written (the log.html will include all the logs from the  run along with a viewer for such logs). 
 - <b>`log_html_style`</b>:  The style to be used for the log.html. 



**Note:**

> It's Ok to add more than one log output, but if 2 log outputs point to the same directory there will be conflicts (in the future this should generate an error). 


---

<a href="..\..\log\src\robocorp\log\__init__.py#L879"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square" /></a>

## <kbd>function</kbd> `close_log_outputs`

```python
close_log_outputs()
```

This method must be called to close loggers. 

Note that some loggers such as the one which outputs html needs to bo closed to actually write the output. 


---

<a href="..\..\log\src\robocorp\log\__init__.py#L892"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square" /></a>

## <kbd>function</kbd> `add_in_memory_log_output`

```python
add_in_memory_log_output(write: Callable[[str], Any])
```

Adds a log output which is in-memory (receives a callable). 



**Args:**
 
 - <b>`write`</b>:  A callable which will be called as `write(msg)` whenever a message is sent from the logging. 



**Returns:**
 A context manager which can be used to automatically remove and close the related logger. 


---

<a href="..\..\log\src\robocorp\log\__init__.py#L166"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square" /></a>

## <kbd>class</kbd> `ConsoleMessageKind`










---

_This file was automatically generated via [lazydocs](https://github.com/ml-tooling/lazydocs)._
