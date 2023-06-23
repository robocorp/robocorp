import datetime
import functools
import sys
import threading
import traceback
from pathlib import Path
from typing import Any, Optional, Sequence, Tuple, Union

from .protocols import LogElementType, LogHTMLStyle, OptExcInfo


class _LogErrorLock:
    tlocal = threading.local()


def _log_error(func):
    @functools.wraps(func)
    def new_func(self, *args, **kwargs) -> Any:
        try:
            return func(self, *args, **kwargs)
        except Exception:
            try:
                writing = _LogErrorLock.tlocal._writing
            except:
                writing = _LogErrorLock.tlocal._writing = False

            if writing:
                # Prevent recursing printing errors.
                return

            _LogErrorLock.tlocal._writing = True
            try:
                traceback.print_exc()
                traceback.print_stack(limit=5)

                robot_output_impl: _RoboLogger = self
                robot_output_impl.log_method_except(sys.exc_info(), True)
            finally:
                _LogErrorLock.tlocal._writing = True

    return new_func


class _RoboLogger:
    def __init__(
        self,
        output_dir: Optional[Union[str, Path]] = None,
        max_file_size: str = "1MB",
        max_files: int = 5,
        log_html: Optional[Union[Path, str]] = None,
        log_html_style: LogHTMLStyle = "standalone",
        min_messages_per_file: int = 50,
        **kwargs,
    ):
        from ._convert_units import _convert_to_bytes
        from ._robo_output_impl import _Config, _RoboOutputImpl

        # Note: expected to be used just when used in-memory (not part of the public API).
        config = _Config(kwargs.get("__uuid__"))
        if log_html_style == "standalone":
            config.log_html_style = 2
        elif log_html_style == "vscode":
            config.log_html_style = 1
        else:
            raise ValueError(f"Unexpected log html style: {log_html_style}")

        if output_dir is None:
            config.output_dir = None
        else:
            config.output_dir = str(output_dir)

        if log_html is None:
            config.log_html = None
        else:
            config.log_html = str(log_html)

        config.max_file_size_in_bytes = _convert_to_bytes(max_file_size)
        config.max_files = max_files

        if min_messages_per_file < 10:
            # Minimum is at least 10 messages per file.
            min_messages_per_file = 10

        config.min_messages_per_file = min_messages_per_file

        if config.max_file_size_in_bytes < _convert_to_bytes("10kb"):
            raise ValueError(
                f"Cannot generate logs where the max file size in bytes is less than 10kb."
                f" Found: {config.max_file_size_in_bytes}."
                f" Arg: {max_file_size}."
            )

        # Note: expected to be used just when used in-memory (not part of the public API).
        config.write = kwargs.get("__write__")
        config.initial_time = kwargs.get("__initial_time__")
        config.additional_info = kwargs.get("__additional_info__")

        self._robot_output_impl = _RoboOutputImpl(config)
        self._skip_log_methods = 0
        self._skip_log_variables = 0

    def hide_from_output(self, string_to_hide: str) -> None:
        self._robot_output_impl.hide_from_output(string_to_hide)

    @property
    def robot_output_impl(self):
        return self._robot_output_impl

    @property
    def initial_time(self) -> datetime.datetime:
        return self._robot_output_impl.initial_time

    def _get_time_delta(self) -> float:
        return self._robot_output_impl.get_time_delta()

    def start_logging_methods(self):
        if self._skip_log_methods <= 0:
            self._robot_output_impl.log_message(
                "ERROR",
                f"_RoboLogger error: start_logging_methods() called before stop_logging_methods() (call is ignored as logging is already on).",
                False,
                __file__,
                sys._getframe().f_lineno,
                self._robot_output_impl.get_time_delta(),
            )
            return

        self._skip_log_methods -= 1

    def stop_logging_methods(self):
        self._skip_log_methods += 1

    def start_logging_variables(self):
        if self._skip_log_variables <= 0:
            self._robot_output_impl.log_message(
                "ERROR",
                f"_RoboLogger error: start_logging_variables() called before stop_logging_variables() (call is ignored as logging is already on).",
                False,
                __file__,
                sys._getframe().f_lineno,
                self._robot_output_impl.get_time_delta(),
            )
            return

        self._skip_log_variables -= 1

    def stop_logging_variables(self):
        self._skip_log_variables += 1

    @_log_error
    def start_run(self, name: str) -> None:
        return self._robot_output_impl.start_run(
            name,
            self._get_time_delta(),
        )

    @_log_error
    def end_run(self, name: str, status: str):
        return self._robot_output_impl.end_run(name, status, self._get_time_delta())

    @_log_error
    def start_task(self, name: str, libname: str, source: str, lineno: int, doc: str):
        return self._robot_output_impl.start_task(
            name,
            libname,
            source,
            lineno,
            doc,
            self._get_time_delta(),
        )

    @_log_error
    def send_info(self, info: str):
        return self._robot_output_impl.send_info(info)

    @_log_error
    def send_start_time_delta(self, time_delta_in_seconds: float):
        if self._skip_log_methods:
            return

        return self._robot_output_impl.send_start_time_delta(time_delta_in_seconds)

    @_log_error
    def end_task(self, name: str, libname: str, status: str, message: str):
        return self._robot_output_impl.end_task(
            name,
            libname,
            status,
            message,
            self._get_time_delta(),
        )

    @_log_error
    def start_element(
        self,
        name: str,
        libname: str,
        source: str,
        lineno: int,
        element_type: LogElementType,
        doc: str,
        args: Sequence[Tuple[str, str, str]],
    ):
        """
        Example:

        start_element(
            "close_browser",
            "RPA.Browser",
            "c:/my/browser.py",
            lineno=1,
            element_type="METHOD",
            doc="Closes Browser",
            args=[("force", "boolean", "True")],
        )
        """
        hide_from_logs = bool(self._skip_log_methods)

        if args:
            if self._skip_log_variables:
                args = []

        return self._robot_output_impl.start_element(
            name,
            libname,
            element_type,
            doc,
            source,
            lineno,
            self._get_time_delta(),
            args,
            hide_from_logs,
        )

    def yield_resume(
        self,
        name: str,
        libname: str,
        source: str,
        lineno: int,
    ):
        hide_from_logs = bool(self._skip_log_methods)

        return self._robot_output_impl.yield_resume(
            name,
            libname,
            source,
            lineno,
            self._get_time_delta(),
            hide_from_logs,
        )

    def yield_suspend(
        self,
        name: str,
        libname: str,
        source: str,
        lineno: int,
        yielded_value_type: str,
        yielded_value_repr: str,
    ):
        if self._skip_log_variables:
            yielded_value_type = ""
            yielded_value_repr = ""

        return self._robot_output_impl.yield_suspend(
            name,
            libname,
            source,
            lineno,
            yielded_value_type,
            yielded_value_repr,
            self._get_time_delta(),
        )

    def yield_from_resume(
        self,
        name: str,
        libname: str,
        source: str,
        lineno: int,
    ):
        hide_from_logs = bool(self._skip_log_methods)

        return self._robot_output_impl.yield_from_resume(
            name,
            libname,
            source,
            lineno,
            self._get_time_delta(),
            hide_from_logs,
        )

    def yield_from_suspend(
        self,
        name: str,
        libname: str,
        source: str,
        lineno: int,
    ):
        return self._robot_output_impl.yield_from_suspend(
            name,
            libname,
            source,
            lineno,
            self._get_time_delta(),
        )

    @_log_error
    def after_assign(
        self,
        name: str,
        libname: str,
        filename: str,
        lineno: int,
        assign_name: str,
        assign_type: str,
        assign_repr: str,
    ):
        if self._skip_log_variables or self._skip_log_methods:
            return

        return self._robot_output_impl.after_assign(
            name,
            libname,
            filename,
            lineno,
            assign_name,
            assign_type,
            assign_repr,
            self._get_time_delta(),
        )

    @_log_error
    def method_return(
        self,
        name: str,
        libname: str,
        filename: str,
        lineno: int,
        return_type: str,
        return_repr: str,
    ):
        if self._skip_log_variables or self._skip_log_methods:
            return

        return self._robot_output_impl.method_return(
            name,
            libname,
            filename,
            lineno,
            return_type,
            return_repr,
            self._get_time_delta(),
        )

    @_log_error
    def end_method(
        self,
        element_type: LogElementType,
        name: str,
        libname: str,
        status: str,
    ):
        return self._robot_output_impl.end_method(
            element_type, name, libname, status, self._get_time_delta()
        )

    @_log_error
    def log_message(
        self,
        level: str,
        message: str,
        html: bool,
        name: str,
        libname: str,
        source: str,
        lineno: int,
    ):
        return self._robot_output_impl.log_message(
            level, message, html, name, libname, source, lineno, self._get_time_delta()
        )

    @_log_error
    def log_method_except(
        self,
        exc_info: OptExcInfo,
        unhandled: bool,
    ):
        # TODO: Improve this: getting the stack and info should be done once
        # outside and then just the messages should be replicated to the actual
        # loggers.
        # Right now we'll do the repr of objects twice for the whole stack...

        hide_vars = bool(self._skip_log_variables or self._skip_log_methods)

        return self._robot_output_impl.log_method_except(exc_info, unhandled, hide_vars)

    @_log_error
    def process_snapshot(
        self,
    ):
        # TODO: Improve this: getting the stack and info should be done once
        # outside and then just the messages should be replicated to the actual
        # loggers.
        # Right now we'll do the repr of objects twice for the whole stack...

        hide_vars = bool(self._skip_log_variables or self._skip_log_methods)

        return self._robot_output_impl.process_snapshot(hide_vars)

    @_log_error
    def console_message(
        self,
        message: str,
        kind: str,
    ):
        return self._robot_output_impl.console_message(
            message, kind, self._get_time_delta()
        )

    @_log_error
    def close(self):
        self.robot_output_impl.close()
