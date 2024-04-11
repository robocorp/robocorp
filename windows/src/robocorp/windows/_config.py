import platform
from contextlib import contextmanager
from typing import Literal

# When trying to execute imports on Mac/Linux.
IS_WINDOWS = platform.system() == "Windows"


class Config:
    """
    The global configurations available in robocorp-windows.

    The API used to get the config is:

    ```python
    from robocorp import windows
    config = windows.config()

    config.simulate_mouse_movement = True
    config.wait_time = .2
    ```
    """

    def __init__(self) -> None:
        # The usual time to wait after some action is done.
        self.wait_time: float = 0.5

        # Defines whether mouse movement should be simulated in
        # the related actions (such as mouse clicking).
        self.simulate_mouse_movement: bool = False

        # When True, errors will be more verbose (this means that execution
        # may be much slower when an error is found)
        # i.e.: if some item is not located, elements beneath the given parent
        # may be printed, which may be slow.
        self.verbose_errors: bool = True

        # When running with robocorp-tasks a screenshot is shown by default
        # if the task fails.
        self.screenshot: Literal["on", "only-on-failure", "off"] = "only-on-failure"

    @property
    def timeout(self) -> float:
        from ._vendored import uiautomation as auto

        # This value can change based on `auto.SetGlobalSearchTimeout(...)` calls.

        return auto.uiautomation.TIME_OUT_SECOND

    @timeout.setter
    def timeout(self, timeout: float) -> None:
        # This value can change based on `auto.SetGlobalSearchTimeout(...)` calls.
        from ._vendored import uiautomation as auto

        auto.uiautomation.TIME_OUT_SECOND = timeout

    @contextmanager
    def disabled_verbose_errors(self):
        """
        Verbose errors are useful but slow, so, if it's expected that errors will
        be thrown at a given location it's possible to use the code below to
        temporarily disable the error verbosity:

        ```python
        from robocorp import windows
        with windows.config().disabled_verbose_errors():
            ... # Operation that may throw ElementNotFound errors.
        ```
        """
        initial = self.verbose_errors
        self.verbose_errors = False
        try:
            yield
        finally:
            self.verbose_errors = initial
