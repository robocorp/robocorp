from contextlib import contextmanager
from io import StringIO
from pathlib import Path

import datetime
import json
import functools
import sys
import threading
import typing
import weakref

from typing import (
    Optional,
    Any,
    Iterator,
    List,
    Sequence,
    Dict,
    Union,
    Iterable,
    Literal,
)
from ._config import Filter, FilterKind
from ._logger_instances import _get_logger_instances
from .protocols import OptExcInfo, LogHTMLStyle, Status
from robo_log.protocols import IReadLines

if typing.TYPE_CHECKING:
    from ._robo_logger import _RoboLogger
    from ._rewrite_filtering import FilesFiltering

__version__ = "0.0.7"
version_info = [int(x) for x in __version__.split(".")]


# --- Logging methods for custom messaging.


def _log(level, message: str, html: bool = False) -> None:
    back_frame = sys._getframe(2)
    source = back_frame.f_code.co_filename
    lineno = back_frame.f_lineno

    for robo_logger in _get_logger_instances():
        robo_logger.log_message(level, message, html, source, lineno)


def critical(message: str, html: bool = False) -> None:
    """
    Adds a new logging message with a critical (error) level.

    Args:
        message: The message which should be logged.
        html: If True the message passed should be rendered as HTML.
    """
    _log(Status.ERROR, message, html)


def warn(message: str, html: bool = False) -> None:
    """
    Adds a new logging message with a warn level.

    Args:
        message: The message which should be logged.
        html: If True the message passed should be rendered as HTML.
    """
    _log(Status.WARN, message, html)


def info(message: str, html: bool = False) -> None:
    """
    Adds a new logging message with an info level.

    Args:
        message: The message which should be logged.
        html: If True the message passed should be rendered as HTML.
    """
    _log(Status.INFO, message, html)


def exception(message: Optional[str] = None, html: bool = False):
    """
    Adds to the logging the exceptions that's currently raised.

    Args:
        message: If given an additional error message to be shown.
        html: If True the message passed should be rendered as HTML.
    """
    if message:
        _log(Status.ERROR, message, html)

    exc_info = sys.exc_info()
    for robo_logger in _get_logger_instances():
        robo_logger.log_method_except(exc_info, unhandled=True)


# --- Methods related to hiding logging information.


@contextmanager
def stop_logging_methods():
    """
    Can be used so that method calls are no longer logged.
    """
    for robo_logger in _get_logger_instances():
        robo_logger.stop_logging_methods()
    try:
        yield
    finally:
        start_logging_methods()


def start_logging_methods():
    """
    Usually doesn't need to be called as `stop_logging_methods` should be used
    as a context manager (which would automatically call this method).

    Can still be used if `stop_logging_methods` with a try..finally if
    `stop_logging_methods` isn't used as a context manager.
    """
    for robo_logger in _get_logger_instances():
        robo_logger.start_logging_methods()


@contextmanager
def stop_logging_variables():
    """
    Can be used so that variables are no longer logged.
    """
    for robo_logger in _get_logger_instances():
        robo_logger.stop_logging_variables()

    try:
        yield
    finally:
        start_logging_variables()


def start_logging_variables():
    """
    Usually doesn't need to be called as `stop_logging_variables` should be used
    as a context manager (which would automatically call this method).

    Can still be used if `stop_logging_variables` with a try..finally if
    `stop_logging_variables` isn't used as a context manager.
    """
    for robo_logger in _get_logger_instances():
        robo_logger.start_logging_variables()


def hide_from_output(string_to_hide: str) -> None:
    """
    Should be called to hide sensitive information from appearing in the output.

    :param string_to_hide:
        The string that should be hidden from the output.
    """
    for robo_logger in _get_logger_instances():
        robo_logger.hide_from_output(string_to_hide)


# --- Logging methods usually called automatically from the framework.


def start_suite(name: str, suite_id: str, suite_source: str) -> None:
    for robo_logger in _get_logger_instances():
        robo_logger.start_suite(name, suite_id, suite_source)


def end_suite(name: str, suite_id: str, status: str) -> None:
    for robo_logger in _get_logger_instances():
        robo_logger.end_suite(name, suite_id, status)


def start_task(name: str, task_id: str, lineno: int, tags: Sequence[str]) -> None:
    for robo_logger in _get_logger_instances():
        robo_logger.start_task(name, task_id, lineno, tags)


def end_task(name: str, task_id: str, status: str, message: str) -> None:
    for robo_logger in _get_logger_instances():
        robo_logger.end_task(name, task_id, status, message)


def iter_decoded_log_format_from_stream(stream: IReadLines) -> Iterator[dict]:
    """
    :param stream:
        The stream which should be iterated in (anything with a `readlines()` method).

    :returns:
        An iterator which will decode the messages and provides a dictionary for
        each message found.

        Example of messages provided:

        {'message_type': 'V', 'version': '1'}
        {'message_type': 'T', 'initial_time': '2022-10-31T07:45:57.116'}
        {'message_type': 'ID', 'part': 1, 'id': 'gen-from-output-xml'}
        {'message_type': 'SS', 'name': 'Robot Check', 'suite_id': 's1', 'suite_source': 'x:\\vscode-robot\\local_test\\robot_check', 'time_delta_in_seconds': 0.3}
        {'message_type': 'ST', 'name': 'My task', 'suite_id': 's1-s1-t1', 'lineno': 5, 'time_delta_in_seconds': 0.2}
    """
    from ._decoder import iter_decoded_log_format

    return iter_decoded_log_format(stream)


def iter_decoded_log_format_from_log_html(log_html: Path) -> Iterator[dict]:
    """
    This function will read the chunks saved in the log html and provide
    an iterator which will provide the messages which were encoded into it.

    :returns:
        An iterator which will decode the messages and provides a dictionary for
        each message found.

        Example of messages provided:

        {'message_type': 'V', 'version': '1'}
        {'message_type': 'T', 'initial_time': '2022-10-31T07:45:57.116'}
        {'message_type': 'ID', 'part': 1, 'id': 'gen-from-output-xml'}
        {'message_type': 'SS', 'name': 'Robot Check', 'suite_id': 's1', 'suite_source': 'x:\\vscode-robot\\local_test\\robot_check', 'time_delta_in_seconds': 0.3}
        {'message_type': 'ST', 'name': 'My task', 'suite_id': 's1-s1-t1', 'lineno': 5, 'time_delta_in_seconds': 0.2}

    """
    import zlib
    import base64
    from ast import literal_eval

    txt = log_html.read_text(encoding="utf-8")
    i = txt.find("let chunks = [")
    j = txt.find("];", i)

    if i < 0 or j < 0:
        # It may be that we're in dev mode and the target should be the bundle.js
        bundle_js = log_html.parent / "bundle.js"
        if bundle_js.exists():
            txt = bundle_js.read_text(encoding="utf-8")
            i = txt.find("let chunks = [")
            j = txt.find("];", i)

    assert i > 0, "Could not find the chunks in the file."
    assert j > 0, "Could not find the end of the chunks in the file."

    sub = txt[i + len("let chunks = ") : j + 1]
    # We have something as:
    # ['base64strZippedStr', 'base64strZippedStr']
    # so, at this point decode it and unzip it
    lst = literal_eval(sub)

    stream = StringIO()
    for s in lst:
        decoded = zlib.decompress(base64.b64decode(s))
        stream.write(decoded.decode("utf-8"))

    stream.seek(0)
    yield from iter_decoded_log_format_from_stream(stream)


def verify_log_messages_from_messages_iterator(
    messages_iterator: Iterator[dict], expected: Sequence[dict]
) -> List[dict]:
    """
    A helper for checking that the expected messages are found in the
    given messages iterator.

    Args:
        messages_iterator: An
        expected:

    Example:

    """
    expected_lst: List[dict] = list(expected)
    log_messages = list(messages_iterator)
    log_msg: dict
    for log_msg in log_messages:
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
    s: str, expected: Sequence[dict]
) -> List[dict]:
    log_messages: List[dict] = []
    for log_msg in s.splitlines():
        log_msg_dict: dict = json.loads(log_msg.strip())
        log_messages.append(log_msg_dict)

    return verify_log_messages_from_messages_iterator(iter(log_messages), expected)


def verify_log_messages_from_log_html(
    log_html: Path, expected: Sequence[dict]
) -> List[dict]:
    iter_in = iter_decoded_log_format_from_log_html(log_html)
    return verify_log_messages_from_messages_iterator(iter_in, expected)


def verify_log_messages_from_stream(
    stream: IReadLines, expected: Sequence[dict]
) -> Sequence[dict]:
    return verify_log_messages_from_messages_iterator(
        iter_decoded_log_format_from_stream(stream), expected
    )


def setup_auto_logging(
    tracked_folders: Optional[Sequence[Union[Path, str]]] = None,
    untracked_folders: Optional[Sequence[Union[Path, str]]] = None,
    filters: Sequence[Filter] = (),
):
    """
    :param tracked_folders:
        The folders which must be tracked (by default any folder in the
        pythonpath which is not in a python-library folder).

    :param untracked_folders:
        The folders which must not be tracked (by default any folder which is a
        python-library folder).

    :param filters:
        Additional filters to add folders/modules to be tracked.

        i.e.:

        [
            Filter("mymodule.ignore", exclude=True, is_path=False),
            Filter("mymodule.rpa", exclude=False, is_path=False),
            Filter("**/check/**", exclude=True, is_path=True),
        ]
    """
    from ._config import ConfigFilesFiltering
    from ._auto_logging_setup import register_auto_logging_callbacks

    project_roots: Optional[Sequence[str]]
    if tracked_folders:
        project_roots = [
            (f if isinstance(f, str) else str(f.absolute())) for f in tracked_folders
        ]
    else:
        project_roots = None

    library_roots: Optional[Sequence[str]]
    if untracked_folders:
        library_roots = [
            (f if isinstance(f, str) else str(f.absolute())) for f in untracked_folders
        ]
    else:
        library_roots = None

    return register_auto_logging_callbacks(
        ConfigFilesFiltering(project_roots, library_roots, filters, set_as_global=True)
    )


def add_log_output(
    output_dir: Optional[Union[str, Path]] = None,
    max_file_size: str = "1MB",
    max_files: int = 5,
    log_html: Optional[Union[str, Path]] = None,
    log_html_style: LogHTMLStyle = "standalone",
):
    from ._robo_logger import _RoboLogger  # @Reimport
    from robo_log._auto_logging_setup import OnExitContextManager

    if log_html and not output_dir:
        raise RuntimeError(
            "When log_html is specified, the output_dir must also be specified."
        )

    logger = _RoboLogger(
        output_dir, max_file_size, max_files, log_html, log_html_style=log_html_style
    )
    _get_logger_instances()[logger] = 1

    def _exit():
        _get_logger_instances().pop(logger, None)
        logger.close()

    return OnExitContextManager(_exit)


def close_log_outputs():
    """
    This method must be called to close loggers (note that some loggers such as
    the one which outputs html needs to bo closed to actually write the output).
    """
    while _get_logger_instances():
        logger = next(iter(_get_logger_instances()))
        _get_logger_instances().pop(logger, None)
        logger.close()


def add_in_memory_log_output(write):
    from ._robo_logger import _RoboLogger  # @Reimport
    from robo_log._auto_logging_setup import OnExitContextManager

    logger = _RoboLogger(__write__=write)
    _get_logger_instances()[logger] = 1

    def _exit():
        _get_logger_instances().pop(logger, None)
        logger.close()

    return OnExitContextManager(_exit)


# Not part of the API, used to determine whether a file is a project file
# or a library file when running with the FilterKind.log_on_project_call kind.
# Only set/used when setting up auto-logging (changed at runtime).
def _in_project_roots(filename: str) -> bool:
    return False


def _caller_in_project_roots() -> bool:
    try:
        return _in_project_roots(sys._getframe(2).f_code.co_filename)
    except ValueError:  # call stack is not deep enough
        return False
