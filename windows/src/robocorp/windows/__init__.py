# ruff: noqa: F401
"""
Module used to interact with native widgets on the Windows OS through UI Automation.

This library can be made available by pinning
[![`robocorp-windows`](https://img.shields.io/pypi/v/robocorp-windows?label=robocorp-windows)](https://pypi.org/project/robocorp-windows/)
in your dependencies' configuration.
"""

import time
import typing
from functools import lru_cache
from typing import Callable, List, Literal, Optional, overload

from ._config import Config
from ._control_element import ControlElement
from ._desktop import Desktop
from ._errors import (
    ActionNotPossible,
    ElementDisposed,
    ElementNotFound,
    InvalidLocatorError,
    InvalidStrategyDuplicated,
    ParseError,
)
from ._window_element import WindowElement
from .protocols import Locator

if typing.TYPE_CHECKING:
    from PIL.Image import Image

__version__ = "1.0.4"
version_info = [int(x) for x in __version__.split(".")]


def get_icon_from_file(path: str) -> Optional["Image"]:
    """
    Provides the icon stored in the file of the given path.

    Returns:
        A PIL image with the icon image or None if it was
        not possible to load it.

    Example:

        ```python
        # Get icon from file and convert it to a base64 string
        from robocorp import windows
        from io import BytesIO

        img = windows.get_icon_from_file('c:/temp/my.exe')
        buffered = BytesIO()
        img.save(buffered, format="PNG")
        image_string = base64.b64encode(buffered.getvalue()).decode()
        ```

    Example:

        ```python
        # Get icon from file and save it in the filesystem
        from robocorp import windows

        img = windows.get_icon_from_file('c:/temp/my.exe')

        img.save("c:/temp/my.png", format="PNG")
        ```
    """
    from . import _icon_from_file

    return _icon_from_file.get_icon_from_file(path)


@lru_cache
def __get_cache_mod():
    try:
        from . import _func_robocorp_tasks_cache as mod
    except ImportError:
        # `robocorp-tasks` not available, use implementation that always returns
        # the same instance
        from . import _func_lru_cache as mod  # type:ignore
    return mod


def desktop() -> Desktop:
    """
    Provides the desktop element (which is the root control containing
    top-level windows).

    The elements provided by robocorp-windows are organized as:
        Desktop (root control)
            WindowElement (top-level windows)
                ControlElement (controls inside a window)

    Returns:
        The Desktop element.
    """
    return __get_cache_mod().desktop()


def config() -> "Config":
    """
    Provides an instance to configure the basic settings such as
    the default timeout, whether to simulate mouse movements, showing
    verbose errors on failures, screenshot on error (when running with
    robocorp-tasks), etc.

    Returns:
        Config object to be used to configure the settings.

    Example:

        ```
        from robocorp import windows
        config = windows.config()
        config.verbose_errors = True
        ```
    """
    return __get_cache_mod().config()


@overload
def find_window(
    locator: Locator,
    search_depth: int = ...,
    timeout: Optional[float] = ...,
    wait_time: Optional[float] = ...,
    foreground: bool = ...,
    raise_error: Literal[True] = ...,
) -> "WindowElement":
    ...


@overload
def find_window(
    locator: Locator,
    search_depth: int = ...,
    timeout: Optional[float] = ...,
    wait_time: Optional[float] = ...,
    foreground: bool = ...,
    raise_error: Literal[False] = ...,
) -> Optional["WindowElement"]:
    ...


@overload
def find_window(
    locator: Locator,
    search_depth: int = ...,
    timeout: Optional[float] = ...,
    wait_time: Optional[float] = ...,
    foreground: bool = ...,
    raise_error: bool = ...,
) -> Optional["WindowElement"]:
    ...


def find_window(
    locator: Locator,
    search_depth: int = 1,
    timeout: Optional[float] = None,
    wait_time: Optional[float] = None,
    foreground: bool = True,
    raise_error: bool = True,
) -> Optional["WindowElement"]:
    """
    Finds the first window matching the passed locator.

    Args:
        locator: This is the locator which should be used to find the window.

        search_depth: The search depth to find the window (by default == 1, meaning
            that only top-level windows will be found).

        timeout: The search for a child with the given locator will be retried
            until the given timeout (in **seconds**) elapses.
            At least one full search up to the given depth will always be done
            and the timeout will only take place afterwards.
            If not given the global config timeout will be used.

        wait_time: The time to wait after finding the window. If not passed the
            default value found in the config is used.

        foreground: Whether the found window should be made top-level when found.

        raise_error: Do not raise and return `None` when this is set to `True` and such
            a window isn't found.

    Returns:
        The `WindowElement` which should be used to interact with the window.

    Example:

        ```python
        window = find_window('Calculator')
        window = find_window('name:Calculator')
        window = find_window('subname:Notepad')
        window = find_window('regex:.*Notepad')
        window = find_window('executable:Spotify.exe')
        ```
    """
    return desktop().find_window(
        locator, search_depth, timeout, wait_time, foreground, raise_error
    )


def find_windows(
    locator: Locator = "regex:.*",
    search_depth: int = 1,
    timeout: Optional[float] = None,
    wait_for_window: bool = False,
) -> List["WindowElement"]:
    """
    Finds all windows matching the given locator.

    Args:
        locator: The locator which should be used to find windows (if not
            given, all windows are returned).

        search_depth: The search depth to be used to find windows (by default
            equals 1, meaning that only top-level windows will be found).

        timeout: The search for a child with the given locator will be retried
            until the given timeout (in **seconds**) elapses.
            At least one full search up to the given depth will always be done
            and the timeout will only take place afterwards.
            If not given the global config timeout will be used.
            Only used if `wait_for_window` is True.

        wait_for_window: Defines whether the search should keep on searching
            until a window with the given locator is found (note that if True
            and no window was found a ElementNotFound is raised).

    Returns:
        The `WindowElement`s which should be used to interact with the window.

    Example:

        ```python
        window = find_windows('Calculator')
        window = find_windows('name:Calculator')
        window = find_windows('subname:Notepad')
        window = find_windows('regex:.*Notepad')
        window = find_windows('executable:Spotify.exe')
        ```
    """

    return desktop().find_windows(locator, search_depth, timeout, wait_for_window)


def wait_for_condition(
    condition: Callable[[], bool],
    timeout: float = 8.0,
    msg: Optional[Callable[[], str]] = None,
):
    """
    A helper function to wait for some condition.
    Args:
        condition: The condition to be waited for.
        timeout: The time to wait for the condition.
        msg: An optional message to be shown in the exception if the condition
            is not satisfied.

    Raises:
        TimeoutError: If the condition was not satisfied in the given timeout.

    Example:

        ```python
        from robocorp import windows

        calc_window = windows.find_window("name:Calculator")
        calc_window.click("Close Calculator")
        windows.wait_for_condition(calc_window.is_disposed)
        ```
    """
    if msg is None:

        def msg():
            return f"Condition not reached in {timeout} seconds."

    initial_time = time.monotonic()
    timeout = 8
    while True:
        if condition():
            break
        if time.monotonic() - initial_time > timeout:
            raise TimeoutError(msg())
        time.sleep(1 / 10)


__all__ = [
    "Desktop",
    "ActionNotPossible",
    "ElementDisposed",
    "ElementNotFound",
    "InvalidLocatorError",
    "InvalidStrategyDuplicated",
    "ParseError",
    "Locator",
    "get_icon_from_file",
    "desktop",
    "config",
    "find_window",
    "find_windows",
    "wait_for_condition",
    # These cannot be instantiated by the client, but they're available
    # for isinstance/type checking.
    "WindowElement",
    "ControlElement",
]
