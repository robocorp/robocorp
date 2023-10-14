from typing import Literal


class Config:
    """
    The global configurations available in robocorp-windows.

    The API used to get the config is:

    ```python
    from robocorp import windows
    config = windows.config()
    ```
    """

    def __init__(self) -> None:
        # The usual time to wait after some action is done.
        self.wait_time: float = 0.5

        # Defines whether mouse movement should be simulated in
        # the related actiosn (such as mouse clicking).
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
        # This value can change based on `auto.SetGlobalSearchTimeout(...)` calls.
        import robocorp.windows.vendored.uiautomation as auto

        return auto.uiautomation.TIME_OUT_SECOND

    @timeout.setter
    def timeout(self, timeout: float) -> None:
        # This value can change based on `auto.SetGlobalSearchTimeout(...)` calls.
        import robocorp.windows.vendored.uiautomation as auto

        auto.uiautomation.TIME_OUT_SECOND = timeout
