import subprocess
from typing import Iterator, Optional

import pytest

from robocorp.windows import config, wait_for_condition
from robocorp.windows._window_element import WindowElement


def wait_for_process_exit(popen: subprocess.Popen, timeout=8):
    wait_for_condition(
        lambda: popen.poll() is not None,
        timeout=8,
        msg=lambda: f"Process did not close in {timeout} seconds.",
    )


@pytest.fixture(autouse=True)
def config_verbose_logging():
    config().verbose_errors = True


@pytest.fixture
def tk_process() -> Iterator[subprocess.Popen]:
    """
    Note: kills existing tk processes prior to starting.
    """
    import sys

    from robocorp_windows_tests import snippet_tk

    from robocorp.windows import find_window, find_windows
    from robocorp.windows._processes import kill_process_and_subprocesses

    # Ensure no tk processes when we start...
    windows_found = list(
        x for x in find_windows() if x.name == "Tkinter Elements Showcase"
    )
    for w in windows_found:
        kill_process_and_subprocesses(w.ui_automation_control.ProcessId)

    f = snippet_tk.__file__
    popen = subprocess.Popen([sys.executable, f])

    # i.e.: wait for it to be visible
    find_window('name:"Tkinter Elements Showcase"', timeout=20)

    yield popen
    if popen.poll() is None:
        kill_process_and_subprocesses(popen.pid)


@pytest.fixture
def calc_process() -> Iterator[subprocess.Popen]:
    """
    Note: kills existing calculators prior to starting.
    """
    from robocorp import windows
    from robocorp.windows._processes import kill_process_and_subprocesses

    # Ensure no calculators when we start...
    windows.desktop().close_windows("name:Calculator")

    import os

    calc_path = "C:\\Windows\\System32\\calc.exe"
    assert os.path.exists(calc_path)

    popen = subprocess.Popen(calc_path)
    yield popen
    kill_process_and_subprocesses(popen.pid)

    # Note: the pid from the popen is not the same as what we'd expect for the
    # calculator (it actually spawns under a different pid).
    windows.desktop().close_windows("name:Calculator")


@pytest.fixture
def calculator_window_element(calc_process) -> Iterator[WindowElement]:
    from robocorp import windows

    calculator_window_element: Optional[WindowElement] = None
    calculator_window_element = windows.find_window(
        "name:Calculator", timeout=10, wait_time=0
    )
    assert calculator_window_element
    yield calculator_window_element


@pytest.fixture
def notepad_window():
    """Opens a Notepad window using Windows search and closes it by process."""
    from robocorp import windows

    desktop = windows.Desktop()
    desktop.windows_run("notepad")
    notepad_win = windows.find_window("class:Notepad subname:Notepad")

    yield notepad_win

    notepad_win.close_window()
