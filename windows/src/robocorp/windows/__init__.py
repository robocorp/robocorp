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

    Sample code to convert it to a base64 string:

        from io import BytesIO
        buffered = BytesIO()
        img.save(buffered, format="PNG")
        image_string = base64.b64encode(buffered.getvalue()).decode()

    Sample code to save it in the filesystem:

        img.save("c:/temp/my.png", format="PNG")
    """
    from robocorp.windows import _icon_from_file

    return _icon_from_file.get_icon_from_file(path)


@lru_cache
def config():
    from ._config import Config

    return Config()


@lru_cache  # Always return the same instance.
def desktop() -> Desktop:
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

        timeout: The timeout to be used for the search.

        wait_time: The time to wait after finding the window. If not passed the
            default value found in the config is used.

        foreground: Whether the found window should be made top-level when found.

    Returns:
        The `WindowElement` which should be used to interact with the window.

    Example:
        window = find_window('Calculator')
        window = find_window('name:Calculator')
        window = find_window('subname:Notepad')
        window = find_window('regex:.*Notepad')
        window = find_window('executable:Spotify.exe')
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
        locator: The locator which should be used to find windows.
        search_depth: The search depth to be used to find windows (by default
            equals 1, meaning that only top-level windows will be found).
        timeout: The timeout to be used to search for windows (note: only
            used if `wait_for_window` is `True`).
        wait_for_window: Defines whether the search should keep on searching
            until a window with the given locator is found (note that if True
            and no window was found an ElementNotFound is raised).

    Returns:
        The `WindowElement` which should be used to interact with the window.
    """

    return desktop().find_windows(locator, search_depth, timeout, wait_for_window)
