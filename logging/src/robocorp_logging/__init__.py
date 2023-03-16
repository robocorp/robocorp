import datetime
import json
from typing import Optional, Any, Iterator, List, Sequence, Dict, Union
import sys
import functools
from io import StringIO
import weakref
from contextlib import contextmanager
from pathlib import Path
import typing

if typing.TYPE_CHECKING:
    from ._logger import _RobocorpLogger

__version__ = "0.0.1"
version_info = [int(x) for x in __version__.split(".")]


def iter_decoded_log_format(stream) -> Iterator[dict]:
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
    yield from iter_decoded_log_format(stream)


# We could use a set, but we're using a dict to keep the order.
__all_logger_instances__: Dict["_RobocorpLogger", int] = {}


from ._rewrite_callbacks import (
    before_method,
    after_method,
    method_return,
)


@contextmanager
def _register_callbacks(rewrite_hook_config):
    # Make sure that this method should be called only once.
    registered = getattr(_register_callbacks, "registered", False)
    if registered:
        return
    _register_callbacks.register = True

    from robocorp_logging._rewrite_hook import RewriteHook

    hook = RewriteHook(rewrite_hook_config)
    sys.meta_path.insert(0, hook)

    def call_before_method(
        package: str, filename: str, name: str, lineno: int, args_dict: dict
    ) -> None:
        args = []
        for key, val in args_dict.items():

            for p in ("password", "passwd"):
                if p in key:
                    for rf_stream in __all_logger_instances__:
                        rf_stream.hide_from_output(val)
                    break

            args.append(f"{key}={val!r}")
        for rf_stream in __all_logger_instances__:
            rf_stream.start_method(
                name,
                package,
                filename,
                lineno,
                "METHOD",
                "",
                args,
                [],
                [],
            )

    def call_after_method(package: str, filename: str, name: str, lineno: int) -> None:
        for rf_stream in __all_logger_instances__:
            rf_stream.end_method(name, package, "PASS", [])

    before_method.register(call_before_method)
    after_method.register(call_after_method)
    try:
        yield
    finally:
        # If the user actually used the with ... statement we'll remove things now.
        # Note: this is meant only for testing as it has caveats (mainly, modules
        # already loaded won't be rewritten and will have the hooks based on
        # the config which was set when it was loaded).
        sys.meta_path.remove(hook)
        before_method.unregister(call_before_method)
        after_method.unregister(call_after_method)


def setup_auto_logging():
    from robocorp_logging._rewrite_config import ConfigFilesFiltering

    return _register_callbacks(ConfigFilesFiltering())


@contextmanager
def add_logging_output(
    output_dir: Optional[str] = None,
    max_file_size: str = "1MB",
    max_files: int = 5,
    log_html: Optional[Union[str, Path]] = None,
):

    from ._logger import _RobocorpLogger  # @Reimport

    logger = _RobocorpLogger(output_dir, max_file_size, max_files, log_html)
    __all_logger_instances__[logger] = 1
    try:
        yield
    finally:
        __all_logger_instances__.pop(logger)
        logger.close()


@contextmanager
def add_in_memory_logging_output(write):

    from ._logger import _RobocorpLogger  # @Reimport

    logger = _RobocorpLogger(__write__=write)
    __all_logger_instances__[logger] = 1
    try:
        yield
    finally:
        __all_logger_instances__.pop(logger)
        logger.close()


# --- Actual logging methods


class Status:
    PASS = "PASS"
    ERROR = "ERROR"
    FAIL = "FAIL"
    INFO = "INFO"
    WARN = "WARN"


def log_start_suite(name: str, suite_id: str, suite_source: str) -> None:
    for rf_stream in __all_logger_instances__:
        rf_stream.start_suite(name, suite_id, suite_source)


def log_end_suite(name: str, suite_id: str, status: str) -> None:
    for rf_stream in __all_logger_instances__:
        rf_stream.end_suite(name, suite_id, status)


def log_start_task(name: str, task_id: str, lineno: int, tags: Sequence[str]):
    for rf_stream in __all_logger_instances__:
        rf_stream.start_task(name, task_id, lineno, tags)


def log_end_task(name: str, task_id: str, status: str, message: str):
    for rf_stream in __all_logger_instances__:
        rf_stream.end_task(name, task_id, status, message)


# --- Methods related to hiding logging information.


@contextmanager
def stop_logging_methods():
    """
    Can be used so that method calls are no longer logged.
    """
    for rf_stream in __all_logger_instances__:
        rf_stream.stop_logging_methods()
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
    for rf_stream in __all_logger_instances__:
        rf_stream.start_logging_methods()


@contextmanager
def stop_logging_variables():
    """
    Can be used so that variables are no longer logged.
    """
    for rf_stream in __all_logger_instances__:
        rf_stream.stop_logging_variables()

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
    for rf_stream in __all_logger_instances__:
        rf_stream.start_logging_variables()


def hide_from_output(string_to_hide: str) -> None:
    """
    Should be called to hide sensitive information from appearing in the output.

    :param string_to_hide:
        The string that should be hidden from the output.
    """
    for rf_stream in __all_logger_instances__:
        rf_stream.hide_from_output(string_to_hide)
