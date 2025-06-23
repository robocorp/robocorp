import enum
import json
import sys
import threading
import typing
from collections.abc import MutableSet
from contextlib import contextmanager, nullcontext
from io import StringIO
from pathlib import Path
from types import TracebackType
from typing import (
    IO,
    Any,
    Callable,
    Dict,
    Iterator,
    List,
    Literal,
    Optional,
    Protocol,
    Sequence,
    Union,
    overload,
)

from . import _config
from ._log_redacter import _log_redacter
from ._logger_instances import _get_logger_instances

# Not part of the API, used to determine whether a file is a project file
# or a library file when running with the FilterKind.log_on_project_call kind.
from ._rewrite_filtering import FilesFiltering as _FilesFiltering
from ._sensitive_variable_names import _sensitive_names
from ._suppress_helper import SuppressHelper as _SuppressHelper
from .protocols import IReadLines, LogHTMLStyle, Status

if typing.TYPE_CHECKING:
    from ._robo_logger import _RoboLogger

__version__ = "3.0.1"
version_info = [int(x) for x in __version__.split(".")]

# --- Export parts of the public API below (imports above aren't part of
# the public API).

Filter = _config.Filter
FilterKind = _config.FilterKind

# Note: clients are not meant to instance this class, it's just meant to be
# available for typing.
AutoLogConfigBase = _config.AutoLogConfigBase

# Subclass of the AutoLogConfigBase. Clients are expected to instance it to
# configure auto-logging.
DefaultAutoLogConfig = _config.DefaultAutoLogConfig

# --- Logging methods for custom messaging.


def _log(level, message: Sequence[Any], html: bool = False) -> None:
    accept_in_log = _config._general_log_config.accept_log_level(level)
    accept_in_output = _config._general_log_config.accept_output_log_level(level)
    if not accept_in_log and not accept_in_output:
        return

    m = " ".join(str(x) for x in message)

    if accept_in_log:
        back_frame = sys._getframe(2)
        f_code = back_frame.f_code
        source = f_code.co_filename
        name = f_code.co_name
        lineno = back_frame.f_lineno
        libname = str(back_frame.f_globals.get("__package__", ""))

        name, libname, source, lineno

        robo_logger: "_RoboLogger"
        with _get_logger_instances() as logger_instances:
            for robo_logger in logger_instances:
                robo_logger.log_message(level, m, html, name, libname, source, lineno)

    if not html:  # html messages are never put in the output.
        if accept_in_output:
            s = _config._general_log_config.get_output_stream_name(level)
            try:
                writing = _ConsoleMessagesLock.tlocal._writing
            except Exception:
                writing = _ConsoleMessagesLock.tlocal._writing = False

            if writing:
                return
            _ConsoleMessagesLock.tlocal._writing = True
            try:
                if s == "stdout":
                    print(m)
                elif s == "stderr":
                    print(m, file=sys.stderr)
                else:
                    raise RuntimeError(f"Unexpected output stream name: {s}")
            finally:
                _ConsoleMessagesLock.tlocal._writing = False


def critical(*message: Any) -> None:
    """
    Adds a new logging message with a critical (error) level.

    Args:
        message: The message which should be logged.

    Example:
        ```python
        critical('Failed because', obj, 'is not', expected)
        ```

    Note:
        Formatting converts all objects given to `str`. If you need custom
        formatting please pre-format the string.
        i.e.: `critical(f'Failed because {obj!r} is not {expected!r}.')`

    Note:
        A new line is automatically added at the end of the message.

    Note:
        See: `setup_log()` for configurations which may filter out the logged
        calls and also print it to a stream (such stdout/stderr).
    """
    _log(Status.ERROR, message)


def warn(*message: Any) -> None:
    """
    Adds a new logging message with a warn level.

    Args:
        message: The message which should be logged.

    Example:
        ```python
        warn('Did not expect', obj)
        ```

    Note:
        Formatting converts all objects given to `str`. If you need custom
        formatting please pre-format the string.
        i.e.: `warn(f'Did not expect {obj!r}.')`

    Note:
        A new line is automatically added at the end of the message.

    Note:
        See: `setup_log()` for configurations which may filter out the logged
        calls and also print it to a stream (such stdout/stderr).
    """
    _log(Status.WARN, message)


def info(*message: Any) -> None:
    """
    Adds a new logging message with an info level.

    Args:
        message: The message which should be logged.


    Example:
        ```python
        info('Received value', obj)
        ```

    Note:
        Formatting converts all objects given to `str`. If you need custom
        formatting please pre-format the string.
        i.e.: `info(f'Received value {obj!r}.')`

    Note:
        A new line is automatically added at the end of the message.

    Note:
        See: `setup_log()` for configurations which may filter out the logged
        calls and also print it to a stream (such stdout/stderr).
    """
    _log(Status.INFO, message)


def debug(*message: Any) -> None:
    """
    Adds a new logging message with an debug level.

    Args:
        message: The message which should be logged.


    Example:
        ```python
        debug('Received value', obj)
        ```

    Note:
        Formatting converts all objects given to `str`. If you need custom
        formatting please pre-format the string.
        i.e.: `debug(f'Received value {obj!r}.')`

    Note:
        A new line is automatically added at the end of the message.

    Note:
        See: `setup_log()` for configurations which may filter out the logged
        calls and also print it to a stream (such stdout/stderr).
    """
    _log(Status.DEBUG, message)


def exception(*message: Any):
    """
    Adds to the logging the exceptions that's currently raised.

    Args:
        message: If given an additional error message to be shown.

    Note:
        In general this method does NOT need to be called as exceptions
        found are automatically tracked by the framework.

    Note:
        A new line is automatically added at the end of the message
        (if a message was given for logging).
    """
    if message:
        _log(Status.ERROR, message)

    exc_info = sys.exc_info()
    with _get_logger_instances() as logger_instances:
        for robo_logger in logger_instances:
            robo_logger.log_method_except(exc_info, unhandled=True)


def html(html: str, level: str = "INFO"):
    """
    Adds html contents to the log.

    Args:
        html: The html content to be embedded in the page.
        level: The level of the message ("INFO", "WARN" or "ERROR")

    Example adding an image:
        ```python
        html(
            '<img src="data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAACwAAAAnBAMAAACGbbfxAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAbUExURR4nOzpCVI+Tnf///+Pk5qqutXN4hVZdbMbJzod39mUAAAAJcEhZcwAADsMAAA7DAcdvqGQAAAETSURBVDjLnZIxT8MwFITPqDQdG1rBGjX8AOBS0hG1ghnUhbFSBlZvMFbqH+fZaeMLBJA4KZHzyb7ce374l1we3vm0Ty/Ix7era1YvSjOeVBWCZx3mveBDwlWyH1OUXM5t0yJqS+4V33xdwWFCrvOoOfmA1r30Z+r9jHV7zmeKd7ADQEOvATkFlzGz13JqIGanYbexYLOldcY+IsniqrEyRrUj7xBwccRm/lSuPqysI3YBjzUfQproNOr/0tLEgE3CK8P2YG54K401XIeWHDw2Uo5H5UP1l1ZXr9+7U2ffRfhTC9HwFVMmqOzl7vTDnEwSvhXsNLaoGbIGurvf97ArhzYbj01sm6TKXm3yC3yX8/hdwCdipl9ujxriXgAAAABJRU5ErkJggg=="/>'
        )
        ```
    """

    assert level in ("ERROR", "WARN", "INFO")
    _log(level, (html,), html=True)


def process_snapshot() -> None:
    """
    Makes a process snapshot and adds it to the logs.

    A process snapshot can include details on the python process and subprocesses
    and should add a thread dump with the stack of all running threads.
    """
    with _get_logger_instances(only_from_main_thread=False) as logger_instances:
        for robo_logger in logger_instances:
            robo_logger.process_snapshot()


class ConsoleMessageKind:
    # Some user message which was being sent to the stdout.
    STDOUT = "stdout"

    # Some user message which was being sent to the stderr.
    STDERR = "stderr"

    # Some regular message (generated by the framework).
    REGULAR = "regular"

    # Some message which deserves a bit more attention (generated by the framework).
    IMPORTANT = "important"

    # The task name is being written (generated by the framework).
    TASK_NAME = "task_name"

    # Some error message (generated by the framework).
    ERROR = "error"

    # Some traceback message (generated by the framework).
    TRACEBACK = "traceback"


class _SentinelUseStdout:
    pass

    def __repr__(self):
        return "_SentinelUseStdout"

    def __str__(self):
        return "_SentinelUseStdout"


class _ConsoleMessagesLock:
    tlocal = threading.local()


def console_message(
    message: str,
    kind: str,
    stream: Union[Optional[IO], _SentinelUseStdout] = _SentinelUseStdout(),
    *,
    flush: Optional[bool] = None,
) -> None:
    """
    Shows a message in the console and also adds it to the log output.

    Args:
        message: The message to be added to the log.
        kind:
            User messages (note: the redirect feature which would add these
                automatically -- if that's the case, the 'stream' would need
                to be None so that it's not written again):
            "stdout": Some user message which was being sent to the stdout.
            "stderr": Some user message which was being sent to the stderr.

            Messages from the framework:
            "regular": Some regular message.
            "important": Some message which deserves a bit more attention.
            "task_name": The task name is being written.
            "error": Some error message.
            "traceback": Some traceback message.
        stream: If specified this is the stream where the message should
            also be written.
            - if not specified (_SentinelUseStdout) it's written to sys.stdout by default.
            - if None it's not written.
        flush: Whether we should flush after sending the message (if None
               it's flushed if the end char ends with '\n').
    """
    from ._safe_write_to_stream import safe_write_to_stream

    try:
        writing = _ConsoleMessagesLock.tlocal._writing
    except Exception:
        writing = _ConsoleMessagesLock.tlocal._writing = False

    if writing:
        return
    _ConsoleMessagesLock.tlocal._writing = True

    try:
        robo_logger: "_RoboLogger"
        with _get_logger_instances() as logger_instances:
            for robo_logger in logger_instances:
                robo_logger.console_message(message, kind)

        if isinstance(stream, _SentinelUseStdout):
            stream = sys.stdout

        if stream is not None:
            stream = typing.cast(IO, stream)

            from . import console

            ctx: Any

            if kind in (ConsoleMessageKind.ERROR, ConsoleMessageKind.STDERR):
                ctx = console.set_color(console.COLOR_RED)

            elif kind in (ConsoleMessageKind.IMPORTANT, ConsoleMessageKind.TASK_NAME):
                ctx = console.set_color(console.COLOR_CYAN)

            elif kind == ConsoleMessageKind.TRACEBACK:
                ctx = console.set_color(console.COLOR_RED)

            else:
                ctx = nullcontext()

            with ctx:
                safe_write_to_stream(stream, message)

            if flush is None:
                flush = message.endswith("\n")

            if flush:
                stream.flush()
    finally:
        _ConsoleMessagesLock.tlocal._writing = False


# --- Methods related to hiding logging information.


@contextmanager
def _suppress_contextmanager(variables=True, methods=True):
    with _get_logger_instances() as logger_instances:
        for robo_logger in logger_instances:
            if variables:
                robo_logger.stop_logging_variables()
            if methods:
                robo_logger.stop_logging_methods()

    try:
        yield
    finally:
        with _get_logger_instances() as logger_instances:
            for robo_logger in logger_instances:
                if variables:
                    robo_logger.start_logging_variables()
                if methods:
                    robo_logger.start_logging_methods()


_suppress_helper = _SuppressHelper(_suppress_contextmanager)


def suppress_methods():
    """
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
    """
    return suppress(variables=False, methods=True)


def suppress_variables():
    """
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
    """
    return suppress(variables=True, methods=False)


class _AnyCallOrCtxManager(Protocol):
    def __call__(self, *args, **kwargs) -> Any:
        pass

    def __enter__(self) -> Any:
        """Return `self` upon entering the runtime context."""

    def __exit__(self, exc_type, exc_value, traceback) -> None:
        """Raise any exception triggered within the runtime context."""


@overload
def suppress(*, variables: bool = True, methods: bool = True) -> _AnyCallOrCtxManager:
    """
    Arguments when used as a decorator or context manager with parameters.

    Suppresses everything except the arguments marked as "False"
    """


@overload
def suppress(func: Callable[[], Any]) -> _AnyCallOrCtxManager:
    """
    Arguments when used as a decorator without any arguments
    -- just receives it as a function.
    """


def suppress(*args, **kwargs):
    """
    API to suppress logging to be used as a context manager or decorator.

    By default suppresses everything and its actual API is something as:

    def suppress(variables:bool = True, methods:bool = True):
        ...

    Args:
        variables: Whether variables should be suppressed in the scope.

        methods: Whether method calls should be suppressed in the scope.

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
    """
    return _suppress_helper.handle(*args, **kwargs)


def is_sensitive_variable_name(variable_name: str) -> bool:
    """
    Returns true if the given variable name should be considered sensitive.

    Args:
        variable_name: The variable name to be checked.

    Returns:
        True if the given variable name is considered to be sensitive (in which
        case its value should be redacted) and False otherwise.
    """
    return _sensitive_names.is_sensitive_variable_name(variable_name)


def add_sensitive_variable_name(variable_name: str) -> None:
    """
    Marks a given variable name as sensitive

    (in this case any variable containing the given `variable_name` will be
    redacted).

    Note that this will add a patterns where any variable containing the given
    variable name even as a substring will be considered sensitive.

    Args:
        variable_name: The variable name to be considered sensitive.
    """
    _sensitive_names.add_sensitive_variable_name(variable_name)


def add_sensitive_variable_name_pattern(variable_name_pattern: str) -> None:
    """
    Adds a given pattern to consider a variable name as sensitive.

    Any variable name matching the given pattern will have its value redacted.

    Args:
        variable_name_pattern: The variable name pattern to be considered
        sensitive.
    """
    _sensitive_names.add_sensitive_variable_name_pattern(variable_name_pattern)


def hide_from_output(string_to_hide: str) -> None:
    """
    Should be called to hide sensitive information from appearing in the output.

    Note that any variable assign or argument which is set to a name containing
    the string:

    'password' or 'passwd'

    Will be automatically hidden and it's also possible to add new names to
    be automatically redacted withe the methods: `add_sensitive_variable_name`
    and `add_sensitive_variable_name_pattern`.

    Args:
        string_to_hide: The string that should be hidden from the output.
    """

    _log_redacter.hide_from_output(string_to_hide)


class IRedactConfiguration(Protocol):
    @property
    def dont_hide_strings(self) -> MutableSet[str]:
        """
        This provides the set of strings that should not be hidden from the
        logs.

        The default strings that should not be hidden are:
        'None', 'True', 'False'
        """

    @property
    def hide_strings(self) -> MutableSet[str]:
        """
        This provides the set of strings that should be hidden from the logs.
        """

    # Strings smaller than this value won't be redacted in the logs.
    # Default value 2 means that strings with 1 or 2 chars will never be
    # hidden from the logs.
    dont_hide_strings_smaller_or_equal_to: int = 2


def hide_strings_config() -> IRedactConfiguration:
    """
    Can be used to configure heuristics on what should be hidden and what
    should not be hidden from the logs.

    Example:
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
    """
    return _log_redacter.config


# --- Logging methods usually called automatically from the framework.


def start_run(name: str) -> None:
    """
    Starts a run session (adds the related event to the log).

    Args:
        name: The name of the run.

    Note: robocorp-tasks calls this method automatically.
    """
    with _get_logger_instances() as logger_instances:
        for robo_logger in logger_instances:
            robo_logger.start_run(name)


def end_run(name: str, status: str) -> None:
    """
    Finishes a run session (adds the related event to the log).

    Args:
        name: The name of the run.
        status: The run status.

    Note: robocorp-tasks calls this method automatically.
    """
    with _get_logger_instances() as logger_instances:
        for robo_logger in logger_instances:
            robo_logger.end_run(name, status)


def start_task(
    name: str, libname: str, source: str, lineno: int, doc: str = ""
) -> None:
    """
    Starts a task (adds the related event to the log).

    Args:
        name: The name of the task.
        libname: The library (module name) where the task is defined.
        source: The source of the task.
        lineno: The line number of the task in the given source.
        doc: The documentation for the task.

    Note: robocorp-tasks calls this method automatically.
    """
    with _get_logger_instances() as logger_instances:
        for robo_logger in logger_instances:
            robo_logger.start_task(name, libname, source, lineno, doc)


def end_task(name: str, libname: str, status: str, message: str) -> None:
    """
    Ends a task (adds the related event to the log).

    Args:
        name: The name of the task.
        libname: The library (module name) where the task is defined.
        status: The pass/fail status of the task
        message: The message for a failed task

    Note: robocorp-tasks calls this method automatically.
    """
    with _get_logger_instances() as logger_instances:
        for robo_logger in logger_instances:
            robo_logger.end_task(name, libname, status, message)


# ---- APIs to decode existing log files


def iter_decoded_log_format_from_stream(stream: IReadLines) -> Iterator[dict]:
    """
    Iterates stream contents and decodes those as dicts.

    Args:
        stream: The stream which should be iterated in (anything with a
            `readlines()` method which should provide the messages encoded
            in the internal format).

    Returns:
        An iterator which will decode the messages and provides a dictionary for
        each message found.

        Example of messages provided:

        ```python
        {'message_type': 'V', 'version': '1'}
        {'message_type': 'T', 'time': '2022-10-31T07:45:57.116'}
        {'message_type': 'ID', 'part': 1, 'id': 'gen-from-output-xml'}
        {'message_type': 'SR', 'name': 'Robot Check', 'time_delta_in_seconds': 0.3}
        ...
        ```

        Note: the exact format of the messages provided is not stable across
        releases.
    """
    from ._decoder import iter_decoded_log_format

    return iter_decoded_log_format(stream)


def iter_decoded_log_format_from_log_html(log_html: Path) -> Iterator[dict]:
    """
    Reads the data saved in the log html and provides decoded messages (dicts).

    Returns:
        An iterator which will decode the messages and provides a dictionary for
        each message found.

        Example of messages provided:

        ```python
        {'message_type': 'V', 'version': '1'}
        {'message_type': 'T', 'time': '2022-10-31T07:45:57.116'}
        {'message_type': 'ID', 'part': 1, 'id': 'gen-from-output-xml'}
        {'message_type': 'SR', 'name': 'Robot Check', 'time_delta_in_seconds': 0.3}
        ...
        ```

        Note: the exact format of the messages provided is not stable across
        releases.
    """

    txt = log_html.read_text(encoding="utf-8")
    return iter_decoded_log_format_from_log_html_contents(txt, log_html)


def iter_decoded_log_format_from_log_html_contents(
    log_html_contents: str, log_html: Optional[Path] = None
) -> Iterator[dict]:
    """
    Reads the data saved in the log html and provides decoded messages (dicts).

    Returns:
        An iterator which will decode the messages and provides a dictionary for
        each message found.

        Example of messages provided:

        ```python
        {'message_type': 'V', 'version': '1'}
        {'message_type': 'T', 'time': '2022-10-31T07:45:57.116'}
        {'message_type': 'ID', 'part': 1, 'id': 'gen-from-output-xml'}
        {'message_type': 'SR', 'name': 'Robot Check', 'time_delta_in_seconds': 0.3}
        ...
        ```

        Note: the exact format of the messages provided is not stable across
        releases.
    """
    import base64
    import zlib
    from ast import literal_eval

    i = log_html_contents.find("let chunks = [")
    j = log_html_contents.find("];", i)

    if i < 0 or j < 0:
        # It may be that we're in dev mode and the target should be the bundle.js
        if log_html is None:
            raise AssertionError("Unable to find chunks in log html contents.")

        bundle_js = log_html.parent / "bundle.js"
        if bundle_js.exists():
            log_html_contents = bundle_js.read_text(encoding="utf-8")
            i = log_html_contents.find("let chunks = [")
            j = log_html_contents.find("];", i)

    assert (
        i > 0
    ), f"Could not find the chunks in the file ({log_html or '<log_html_not_provided>'})."
    assert j > 0, "Could not find the end of the chunks in the file."

    sub = log_html_contents[i + len("let chunks = ") : j + 1]
    # We have something as:
    # ['base64strZippedStr', 'base64strZippedStr']
    # so, at this point decode it and unzip it
    lst = literal_eval(sub)

    stream = StringIO()
    for s in lst:
        decoded = zlib.decompress(base64.b64decode(s))
        stream.write(decoded.decode("utf-8"))

    stream.seek(0)
    # Uncomment to see contents loaded.
    # print(stream.getvalue())
    yield from iter_decoded_log_format_from_stream(stream)


_DEFAULT_NOT_EXPECTED: Sequence[dict] = ({"message_type": "L", "level": "E"},)


def verify_log_messages_from_messages_iterator(
    messages_iterator: Iterator[dict],
    expected: Sequence[dict],
    not_expected: Sequence[dict] = _DEFAULT_NOT_EXPECTED,
) -> List[dict]:
    """
    Helper for checking that the expected messages are found in the given messages iterator.

    Can also check if a message is not found.

    Args:
        messages_iterator: An iterator over the messages found.
        expected: The messages which are expected to be found. If some message
            expected to be found is not found an AssertionError will be raised.
        not_expected: The messages that should not appear.

    Example:
        ```python
        verify_log_messages_from_messages_iterator(
        messages_iterator,
        [
            {'message_type': 'V', 'version': '1'}
            {'message_type': 'T', 'time': '2022-10-31T07:45:57.116'}
        ]
        ```

    Note: if one of the key entries is `__check__` the value will be considered
    a callable which should return `True` or `False` to determine if a match was
    made.

    Example:
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
    """
    expected_lst: List[dict] = list(expected)
    log_messages = list(messages_iterator)
    log_msg: dict
    for log_msg in log_messages:
        for not_expected_dct in not_expected:
            for key, val in not_expected_dct.items():
                if key == "__check__":
                    if not val(log_msg):
                        break

                elif log_msg.get(key) != val:
                    break
            else:
                new_line = "\n"
                raise AssertionError(
                    f"Found unexpected message: {not_expected_dct}.\nFound:\n{new_line.join(str(x) for x in log_messages)}"
                )

        for expected_dct in expected_lst:
            for key, val in expected_dct.items():
                if key == "__check__":
                    if not val(log_msg):
                        break

                elif log_msg.get(key) != val:
                    break
            else:
                expected_lst.remove(expected_dct)
                break

    if expected_lst:
        new_line = "\n"
        raise AssertionError(
            f"Did not find {expected_lst}.\nFound:\n{new_line.join(str(x) for x in log_messages)}"
        )
    return log_messages


def verify_log_messages_from_decoded_str(
    s: str,
    expected: Sequence[dict],
    not_expected: Sequence[dict] = _DEFAULT_NOT_EXPECTED,
) -> List[dict]:
    """
    Verifies whether the given messages are available or not in the decoded messages.

    Args:
        s: A string with the messages already decoded (where messages are
        separated by lines and each message is a json string to be decoded).
        expected: The messages expected.
        not_expected: The messages that should not appear.

    See: `verify_log_messages_from_messages_iterator` for more details on the
        matching of messages.
    """
    log_messages: List[dict] = []
    for log_msg in s.splitlines():
        stripped = log_msg.strip()
        if stripped:
            try:
                log_msg_dict: dict = json.loads(stripped)
            except Exception:
                raise RuntimeError(f"Error json-loading: >>{stripped}<<")
            log_messages.append(log_msg_dict)

    return verify_log_messages_from_messages_iterator(
        iter(log_messages), expected, not_expected
    )


def _print_msgs_pretty(decoded_msgs: Union[Iterator[dict], Sequence[dict]]) -> None:
    """
    Helper function to print the messages.

    Args:
        decoded_msgs: The messages (already decoded) which should be printed.
    """
    level = 0
    indent = ""

    for m in decoded_msgs:
        msg_type = m["message_type"]
        if msg_type in ("EE", "ET", "ER"):
            level -= 1
            assert level >= 0
            indent = "    " * level

        m = m.copy()
        del m["message_type"]
        print(f"{indent}{msg_type}: {m}")

        if msg_type in ("SE", "ST", "SR"):
            level += 1
            indent = "    " * level


def verify_log_messages_from_log_html(
    log_html: Path,
    expected: Sequence[dict],
    not_expected: Sequence[dict] = _DEFAULT_NOT_EXPECTED,
) -> List[dict]:
    """
    Verifies whether the given messages are available or not in the decoded messages.

    Args:
        log_html: The path to the log_html where messages were embedded.
        expected: The messages expected.
        not_expected: The messages that should not appear.

    See: `verify_log_messages_from_messages_iterator` for more details on the
        matching of messages.
    """
    iter_in = iter_decoded_log_format_from_log_html(log_html)
    return verify_log_messages_from_messages_iterator(iter_in, expected, not_expected)


def verify_log_messages_from_stream(
    stream: IReadLines,
    expected: Sequence[dict],
    not_expected: Sequence[dict] = _DEFAULT_NOT_EXPECTED,
) -> Sequence[dict]:
    """
    Verifies whether the given messages are available or not in the decoded messages.

    Args:
        stream: A stream from where the encoded messages are expected to be read
            from.
        expected: The messages expected.
        not_expected: The messages that should not appear.

    See: `verify_log_messages_from_messages_iterator` for more details on the
        matching of messages.
    """
    return verify_log_messages_from_messages_iterator(
        iter_decoded_log_format_from_stream(stream), expected, not_expected
    )


# --- APIs to setup the logging


class FilterLogLevel(enum.Enum):
    DEBUG = "debug"
    WARN = "warn"
    INFO = "info"
    CRITICAL = "critical"
    NONE = "none"


FilterLogLevelLiterals = Literal["debug", "warn", "info", "critical", "none"]


class IContextManager(Protocol):
    """
    Typing for a "generic" context manager.
    """

    def __enter__(self) -> None:
        pass

    def __exit__(
        self,
        exc_type: Optional[type[BaseException]],
        exc_val: Optional[BaseException],
        exc_tb: Optional[TracebackType],
    ) -> None:
        pass


OutStreamName = Literal["stdout", "stderr"]


def setup_log(
    *,
    max_value_repr_size: Optional[Union[str, int]] = None,
    log_level: Optional[Union[FilterLogLevel, FilterLogLevelLiterals]] = None,
    output_log_level: Optional[Union[FilterLogLevel, FilterLogLevelLiterals]] = None,
    output_stream: Optional[
        Union[
            OutStreamName,
            Dict[
                Union[FilterLogLevel, FilterLogLevelLiterals],
                Union[OutStreamName],
            ],
        ]
    ] = None,
) -> IContextManager:
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

        log_level: Messages with a level higher or equal to the one specified will
            be logged in the `log.html`.

            The default value for this setting is "FilterLogLevel.DEBUG", so,
            any message logged with `log.debug`, `log.info`, `log.warn` and `log.critical`
            will be shown.

        output_log_level: Messages with a level higher or equal to the one specified will
            be printed to the output_stream configured.

            The default value for this setting is "FilterLogLevel.NONE", so,
            any message logged with `log.debug`, `log.info`, `log.warn` and `log.critical`
            is not shown in the output.

        output_stream: It's possible to specify the stream to output contents to
            be printed in the `log.debug`, `log.info`, `log.warn` and `log.critical`
            calls.
            If all messages should be streamed to the same place it can be the output
            stream (or its name) or it can be a dict mapping each level to a different
            stream (or its name).
            Note: if sys.stdout/sys.stderr are used it's preferred to pass it as
            a literal (`"stdout"` or `"stderr"`) as if the stream is redirected it'll
            still print to the current `sys.stdout` / `sys.stderr`.

    Returns:
        A context manager, so, it's possible to use this method with a `with statement`
        so that the configuration is reverted to a previous configuration when
        the context manager exits (if not called with a `with statement` then
        the values won't be reverted).

    Example:

        Setting the max repr size:

        ```python
        from robocorp import log
        # If a repr(obj) returns a string bigger than 100000 chars it'll
        # be clipped to 100000 chars.
        log.setup_log(max_value_repr_size=100_000)
        ```

    Example:

        Configuring to log only `log.critical`:

        ```python
        from robocorp import log
        log.setup_log(log_level=log.FilterLogLevel.CRITICAL)
        ```

    Example:

        Configuring to print log.warn messages to sys.stdout and log.critical
        messages to sys.stderr:

        ```python
        from robocorp import log
        log.setup_log(
            output_log_level='warn',
            output_stream={'warn': 'stdout', 'critical': 'stderr'}
        )
        ```
    """
    prev_values: dict = {}

    if max_value_repr_size:
        from ._convert_units import _convert_to_bytes

        prev_values[
            "max_value_repr_size"
        ] = _config._general_log_config.max_value_repr_size

        _config._general_log_config.max_value_repr_size = _convert_to_bytes(
            max_value_repr_size
        )

    if log_level:
        prev_values["log_level"] = _config._general_log_config.log_level
        if not isinstance(log_level, str):
            log_level = log_level.value  # Received enum.
        _config._general_log_config.log_level = typing.cast(
            FilterLogLevelLiterals, log_level
        )

    if output_log_level:
        prev_values["output_log_level"] = _config._general_log_config.output_log_level
        if not isinstance(output_log_level, str):
            output_log_level = output_log_level.value  # Received enum.
        _config._general_log_config.output_log_level = typing.cast(
            FilterLogLevelLiterals, output_log_level
        )

    if output_stream:
        prev_values["output_stream"] = _config._general_log_config.output_stream
        _config._general_log_config.output_stream = output_stream

    from ._on_exit_context_manager import OnExitContextManager

    def on_exit():
        for k, v in prev_values.items():
            setattr(_config._general_log_config, k, v)

    return OnExitContextManager(on_exit)


def setup_auto_logging(
    config: Optional[AutoLogConfigBase] = None, add_rewrite_hook: bool = True
):
    """
    Sets up automatic logging.

    This must be called prior to actually importing the modules which should
    be automatically logged.

    Args:
        config: The configuration specifying how modules should be automatically
            logged.

            If not passed, by default all files which are library files (i.e.:
            in the python `Lib` or `site-packages`) won't be logged and all files
            which are not library files will be fully logged.

    Returns a context manager which will stop applying the auto-logging to new
    loaded modules. Note that modules which are already being tracked won't
    stop being tracked.
    """
    from ._auto_logging_setup import register_auto_logging_callbacks

    use_config: AutoLogConfigBase
    if config is None:
        # If not passed, use default.
        use_config = DefaultAutoLogConfig()
    else:
        use_config = config

    return register_auto_logging_callbacks(use_config, add_rewrite_hook)


def add_log_output(
    output_dir: Union[str, Path],
    max_file_size: str = "1MB",
    max_files: int = 5,
    log_html: Optional[Union[str, Path]] = None,
    log_html_style: LogHTMLStyle = "standalone",
    min_messages_per_file: int = 50,
):
    """
    Adds a log output which will write the contents to the given output directory.

    Optionally it's possible to collect all the output when the run is finished
    and put it into a log.html file.

    Args:
        output_dir: The output directory where the log contents should be saved.
        max_file_size: The maximum file size for one log file (as a string with
            the value and the unit -- accepted units are: `b`, `kb`, `mb`, `gb`
            if no unit is passed it's considered `b` (bytes)).
            Note that the max size is not a hard guarantee, rather it's a
            guideline that the logging tries to follow (usually it's very close,
            although on degenerate cases it can be considerably different).
        max_files: The maximum amount of files which can be added (if more would
            be needed the oldest one is erased).
        log_html: If given this is the path (file) where the log.html contents
            should be written (the log.html will include all the logs from the
            run along with a viewer for such logs).
        log_html_style: The style to be used for the log.html.
        min_messages_per_file: This is the minimum number of messages that need
            to be added to a file for it to be rotated (if messages are too big
            this may make the max_file_size be surpassed). This is needed to
            prevent a case where a whole new file could be created after just
            a single message if the message was too big for the max file size.

    Note:
        It's Ok to add more than one log output, but if 2 log outputs point
        to the same directory there will be conflicts (in the future this should
        generate an error).
    """
    from ._auto_logging_setup import OnExitContextManager
    from ._robo_logger import _RoboLogger  # @Reimport

    if not output_dir:
        raise RuntimeError("The output directory must be specified.")

    logger = _RoboLogger(
        output_dir,
        max_file_size,
        max_files,
        log_html,
        log_html_style=log_html_style,
        min_messages_per_file=min_messages_per_file,
    )
    with _get_logger_instances() as logger_instances:
        logger_instances[logger] = 1

    def _exit():
        with _get_logger_instances() as logger_instances:
            logger_instances.pop(logger, None)
            logger.close()

    return OnExitContextManager(_exit)


def close_log_outputs():
    """
    This method must be called to close loggers.

    Note that some loggers such as the one which outputs html needs to bo closed
    to actually write the output.
    """
    while True:
        with _get_logger_instances() as logger_instances:
            if logger_instances:
                logger = next(iter(logger_instances))
                logger_instances.pop(logger, None)
                logger.close()
            else:
                break


def add_in_memory_log_output(write: Callable[[str], Any]):
    """
    Adds a log output which is in-memory (receives a callable).

    Args:
        write: A callable which will be called as `write(msg)` whenever
        a message is sent from the logging.

    Returns:
        A context manager which can be used to automatically remove and
        close the related logger.
    """
    from ._auto_logging_setup import OnExitContextManager
    from ._robo_logger import _RoboLogger  # @Reimport

    logger = _RoboLogger(__write__=write)

    with _get_logger_instances() as logger_instances:
        logger_instances[logger] = 1

    def _exit():
        with _get_logger_instances() as logger_instances:
            logger_instances.pop(logger, None)
            logger.close()

    return OnExitContextManager(_exit)


# --- Private APIs


_files_filtering = _FilesFiltering()
_in_project_roots = _files_filtering.in_project_roots


def _caller_in_project_roots(level=2) -> bool:
    try:
        return _in_project_roots(sys._getframe(level).f_code.co_filename)
    except ValueError:  # call stack is not deep enough
        return False
