import datetime
import json
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
import sys
import functools
from io import StringIO
import weakref
from contextlib import contextmanager
from pathlib import Path
import typing
from ._rewrite_config import Filter
import threading
from robocorp_logging.protocols import OptExcInfo, LogHTMLStyle

if typing.TYPE_CHECKING:
    from ._logger import _RobocorpLogger

__version__ = "0.0.3"
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
__tlocal_log__ = threading.local()


def _get_logger_instances() -> Dict["_RobocorpLogger", int]:
    instances: Dict["_RobocorpLogger", int]
    try:
        instances = __tlocal_log__.instances
    except AttributeError:
        instances = __tlocal_log__.instances = {}
    return instances


class _OnExitContextManager:
    def __init__(self, on_exit):
        self.on_exit = on_exit

    def __enter__(self):
        pass

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.on_exit()


def _register_callbacks(rewrite_hook_config):
    # Make sure that this method should be called only once.
    registered = getattr(_register_callbacks, "registered", False)
    if registered:
        import warnings

        warnings.warn("Auto logging is already setup. 2nd call has no effect.")
        return _OnExitContextManager(lambda: None)
    _register_callbacks.registered = True

    tid = threading.get_ident()

    from robocorp_logging._rewrite_hook import RewriteHook
    from ._rewrite_callbacks import (
        before_method,
        after_method,
        method_return,
        method_except,
    )

    hook = RewriteHook(rewrite_hook_config)
    sys.meta_path.insert(0, hook)

    status_stack = []

    def call_before_method(
        package: str,
        mod_name: str,
        filename: str,
        name: str,
        lineno: int,
        args_dict: dict,
    ) -> None:
        if tid != threading.get_ident():
            return

        status_stack.append([package, name, "PASS"])
        args = []
        for key, val in args_dict.items():
            for p in ("password", "passwd"):
                if p in key:
                    for robo_logger in _get_logger_instances():
                        robo_logger.hide_from_output(val)
                    break

            args.append((f"{key}", f"{val!r}"))
        for robo_logger in _get_logger_instances():
            robo_logger.start_element(
                name,
                f"{package}.{mod_name}",
                filename,
                lineno,
                "METHOD",
                "",
                args,
                [],
                [],
            )

    def call_after_method(
        package: str, mod_name: str, filename: str, name: str, lineno: int
    ) -> None:
        if tid != threading.get_ident():
            return

        try:
            pop_package, pop_name, status = status_stack.pop(-1)
        except IndexError:
            # oops, something bad happened, the stack is unsynchronized
            log_error("On method return the status_stack was empty.")
            return
        else:
            if pop_package != package or pop_name != name:
                log_error(
                    f"On method return status stack package/name was: {pop_package}.{pop_name}. Received: {package}.{name}."
                )
                return

        for robo_logger in _get_logger_instances():
            robo_logger.end_method(name, f"{package}.{mod_name}", status, [])

    def call_on_method_except(
        package: str,
        mod_name: str,
        filename: str,
        name: str,
        lineno: int,
        exc_info: OptExcInfo,
    ) -> None:
        if tid != threading.get_ident():
            return

        try:
            pop_package, pop_name, _curr_status = status_stack[-1]
        except IndexError:
            # oops, something bad happened, the stack is unsynchronized
            log_error("On method except the status_stack was empty.")
            return

        if pop_package != package or pop_name != name:
            log_error(
                f"On method except status stack package/name was: {pop_package}.{pop_name}. Received: {package}.{name}."
            )
            return
        status_stack[-1][2] = Status.ERROR

        for robo_logger in _get_logger_instances():
            robo_logger.log_method_except(
                f"{package}.{mod_name}", filename, name, lineno, exc_info, False
            )

    before_method.register(call_before_method)
    after_method.register(call_after_method)
    method_except.register(call_on_method_except)

    def _exit():
        # If the user actually used the with ... statement we'll remove things now.
        # Note: this is meant only for testing as it has caveats (mainly, modules
        # already loaded won't be rewritten and will have the hooks based on
        # the config which was set when it was loaded).
        sys.meta_path.remove(hook)
        before_method.unregister(call_before_method)
        after_method.unregister(call_after_method)
        _register_callbacks.registered = False

    return _OnExitContextManager(_exit)


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
    from robocorp_logging._rewrite_config import ConfigFilesFiltering

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

    return _register_callbacks(
        ConfigFilesFiltering(project_roots, library_roots, filters)
    )


def add_log_output(
    output_dir: Optional[Union[str, Path]] = None,
    max_file_size: str = "1MB",
    max_files: int = 5,
    log_html: Optional[Union[str, Path]] = None,
    log_html_style: LogHTMLStyle = "standalone",
):
    from ._logger import _RobocorpLogger  # @Reimport

    if log_html and not output_dir:
        raise RuntimeError(
            "When log_html is specified, the output_dir must also be specified."
        )

    logger = _RobocorpLogger(
        output_dir, max_file_size, max_files, log_html, log_html_style=log_html_style
    )
    _get_logger_instances()[logger] = 1

    def _exit():
        _get_logger_instances().pop(logger, None)
        logger.close()

    return _OnExitContextManager(_exit)


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
    from ._logger import _RobocorpLogger  # @Reimport

    logger = _RobocorpLogger(__write__=write)
    _get_logger_instances()[logger] = 1

    def _exit():
        _get_logger_instances().pop(logger, None)
        logger.close()

    return _OnExitContextManager(_exit)


# --- Actual logging methods


class Status:
    PASS = "PASS"
    ERROR = "ERROR"
    FAIL = "FAIL"
    INFO = "INFO"
    WARN = "WARN"


def log_start_suite(name: str, suite_id: str, suite_source: str) -> None:
    for robo_logger in _get_logger_instances():
        robo_logger.start_suite(name, suite_id, suite_source)


def log_end_suite(name: str, suite_id: str, status: str) -> None:
    for robo_logger in _get_logger_instances():
        robo_logger.end_suite(name, suite_id, status)


def log_start_task(name: str, task_id: str, lineno: int, tags: Sequence[str]) -> None:
    for robo_logger in _get_logger_instances():
        robo_logger.start_task(name, task_id, lineno, tags)


def log_end_task(name: str, task_id: str, status: str, message: str) -> None:
    for robo_logger in _get_logger_instances():
        robo_logger.end_task(name, task_id, status, message)


def log_error(message: str) -> None:
    for robo_logger in _get_logger_instances():
        html = False
        robo_logger.log_message(Status.ERROR, message, html)


def log_info(message: str) -> None:
    for robo_logger in _get_logger_instances():
        html = False
        robo_logger.log_message(Status.INFO, message, html)


def log_warn(message: str) -> None:
    for robo_logger in _get_logger_instances():
        html = False
        robo_logger.log_message(Status.WARN, message, html)


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
