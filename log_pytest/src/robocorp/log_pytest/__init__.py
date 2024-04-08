import os
import sys
from pathlib import Path
from typing import Optional

import pytest
from robocorp.log.protocols import Status
from robocorp.log.pyproject_config import (
    PyProjectInfo,
    read_pyproject_toml,
    read_robocorp_auto_log_config,
)
from robocorp.log.redirect import setup_stdout_logging

from robocorp import log

__version__ = "0.0.4"
version_info = [int(x) for x in __version__.split(".")]


def _setup_log_output(
    output_dir: Path,
    max_file_size: str = "50MB",
    max_files: int = 5,
    log_name: str = "log.html",
):
    # This can be called after user code is imported (but still prior to its
    # execution).
    return log.add_log_output(
        output_dir=output_dir,
        max_file_size=max_file_size,
        max_files=max_files,
        log_html=output_dir / log_name,
    )


class _State:
    """
    This class helps in keeping the state of the log consistent because
    the pytest integration spans multiple hooks.
    """

    # Information on the pyproject.toml
    pyproject_info: Optional[PyProjectInfo] = None

    # 0 if all is ok at the end of the run and 1 otherwise
    exitstatus = 1

    _import_hook_setup = False

    _run_start = 0

    # information on the current test case being run.
    _func_stack: list = []

    # Context managers being tracked for the duration of the run.
    _context_manager_stack: list = []

    @classmethod
    def handle_context_manager(cls, ctx):
        """
        Args:
            ctx: This is a context manager which should be entered
            and exited when the run finishes.
        """
        ctx.__enter__()
        cls._context_manager_stack.append(ctx)

    @classmethod
    def on_run_start(cls):
        cls._run_start += 1
        log.start_run("pytest")
        log.start_task("config and collect", "", "", 0, "")

    @classmethod
    def on_run_end(cls):
        log.end_task("run finished (print results)", "", Status.PASS, "")

        if cls.exitstatus:
            log.end_run("pytest", Status.FAIL)
        else:
            log.end_run("pytest", Status.PASS)

        for ex in reversed(cls._context_manager_stack):
            ex.__exit__(None, None, None)
        del cls._context_manager_stack[:]

        log.close_log_outputs()

    @classmethod
    def _end_config_and_collect_if_needed(cls):
        if cls._run_start:
            log.end_task("config and collect", "", Status.PASS, "")
            cls._run_start = 0

    @classmethod
    def on_start_test(cls, item):
        cls._end_config_and_collect_if_needed()

        cls._func_stack.append(
            [
                item.name,
                item.parent.module.__name__,
                Status.PASS,
                "",
            ]
        )
        log.start_task(
            item.name,
            item.parent.module.__name__,
            item.parent.module.__file__,
            item.function.__code__.co_firstlineno,
            "",
        )

    @classmethod
    def on_end_test(cls, item):
        name, libname, status, message = cls._func_stack.pop(-1)
        log.end_task(name, libname, status, message)

    @classmethod
    def on_run_tests_finished(cls):
        cls._end_config_and_collect_if_needed()
        log.start_task("run finished (print results)", "", "", 0, "")


def pytest_load_initial_conftests(early_config, parser, args):
    # This hook will not be called for conftest.py files, only for setuptools plugins
    # (so, we have pytest_addoption as a 2nd option for the import hook setup).
    _setup_import_hook()


def pytest_addoption(parser: pytest.Parser, pluginmanager):
    parser.addoption(
        "--robocorp-log-output",
        default="./output",
        help=(
            "Defines in which directory the robocorp log output should be saved "
            "(default: ./output)."
        ),
    )

    parser.addoption(
        "--robocorp-log-html-name",
        default="log.html",
        help=("Defines the name of the final log file (default: log.html)."),
    )

    parser.addoption(
        "--robocorp-log-max-file-size",
        default="50MB",
        help=("Defines the max file size (default: 50MB)."),
    )

    parser.addoption(
        "--robocorp-log-max-files",
        default="5",
        help=(
            "Defines the maximum number of files to keep for the logging (default: 5)."
        ),
    )

    _setup_import_hook()


class _ContextErrorReport:
    def show_error(self, message: str):
        pass


def _setup_import_hook() -> None:
    """
    We use one of the early bootstrap modules of pytest because we want to
    setup the auto-logging very early so that we can have our import hook
    code in place when the user loads his code.
    """

    if _State._import_hook_setup:
        return
    _State._import_hook_setup = True

    for mod_name, mod in tuple(sys.modules.items()):
        try:
            f = mod.__file__
        except AttributeError:
            continue
        if f and log._in_project_roots(f):
            log.debug(
                f'The module: "{mod_name}" will not be auto-logged because '
                "it is already loaded."
            )

    # Setup the auto-logging import hook ASAP.
    config: log.AutoLogConfigBase
    pyproject_info = read_pyproject_toml(Path(os.path.abspath(".")))
    if pyproject_info is None:
        config = log.DefaultAutoLogConfig()
    else:
        context = _ContextErrorReport()
        config = read_robocorp_auto_log_config(context, pyproject_info)

    _State.pyproject_info = pyproject_info
    _State.handle_context_manager(log.setup_auto_logging(config))


def pytest_configure(config) -> None:
    output_dir = Path(config.getoption("--robocorp-log-output", "./output"))

    max_file_size: str = config.getoption("--robocorp-log-max-file-size", "50MB")
    max_files: int = int(config.getoption("--robocorp-log-max-files", "5"))
    log_name: str = config.getoption("--robocorp-log-html-name", "log.html")

    _State.handle_context_manager(
        _setup_log_output(
            output_dir,
            max_file_size=max_file_size,
            max_files=max_files,
            log_name=log_name,
        )
    )
    _State.handle_context_manager(setup_stdout_logging(""))
    _State.on_run_start()


def pytest_unconfigure(config):
    _State.on_run_end()


def pytest_sessionfinish(session, exitstatus):
    _State.exitstatus = exitstatus


@pytest.hookimpl(hookwrapper=True)
def pytest_runtest_protocol(item):
    _State.on_start_test(item)
    yield
    _State.on_end_test(item)


@pytest.hookimpl(hookwrapper=True)
def pytest_runtestloop(*args, **kwargs):
    yield
    _State.on_run_tests_finished()


def pytest_runtest_logreport(report):
    if report.failed:
        # Update the status if the test failed.
        if not _State._func_stack:
            log.critical(f"{report.longreprtext}")
        else:
            _curr_stack = _State._func_stack[-1]
            if _curr_stack[2] == Status.PASS:
                _curr_stack[2] = Status.FAIL
                _curr_stack[3] = report.longreprtext
