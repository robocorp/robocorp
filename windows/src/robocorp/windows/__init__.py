"""
The `robocorp-windows` library is a library to be used to interact
with native widgets on the Windows OS.
"""
import typing
from functools import lru_cache
from typing import List, Optional

from robocorp.windows._window_element import WindowElement

from ._desktop import Desktop
from .protocols import Locator

if typing.TYPE_CHECKING:
    from PIL.Image import Image


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
    from robocorp.windows import _icon_from_file

    return _icon_from_file.get_icon_from_file(path)


@lru_cache
def config():
    """
    Provides an instance to configure the basic settings such as
    the default timeout, whether to simulate mouse movements, showing
    verbose errors on failures, etc.

    Returns:
        Config object to be used to configure the settings.

    Example:

        ```
        from robocorp import windows
        config = windows.config()
        config.verbose_errors = True
        ```
    """
    from ._config import Config

    return Config()


@lru_cache  # Always return the same instance.
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
    return Desktop()


def find_window(
    locator: Locator,
    search_depth: int = 1,
    timeout: Optional[float] = None,
    wait_time: Optional[float] = None,
    foreground: bool = True,
) -> WindowElement:
    """
    Finds the first window matching the passed locator.

    Args:
        locator: This is the locator which should be used to find the window.

        search_depth: The search depth to find the window (by default == 1, meaning
            that only top-level windows will be found).

        timeout:
            The search for a child with the given locator will be retried
            until the given timeout elapses.

            At least one full search up to the given depth will always be done
            and the timeout will only take place afterwards.

            If not given the global config timeout will be used.

        wait_time: The time to wait after finding the window. If not passed the
            default value found in the config is used.

        foreground: Whether the found window should be made top-level when found.

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
    return desktop().find_window(locator, search_depth, timeout, wait_time, foreground)


def find_windows(
    locator: Locator = "regex:.*",
    search_depth: int = 1,
    timeout: Optional[float] = None,
    wait_for_window: bool = False,
) -> List[WindowElement]:
    """
    Finds all windows matching the given locator.

    Args:
        locator: The locator which should be used to find windows (if not
            given, all windows are returned).

        search_depth: The search depth to be used to find windows (by default
            equals 1, meaning that only top-level windows will be found).

        timeout:
            The search for a child with the given locator will be retried
            until the given timeout elapses.

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
