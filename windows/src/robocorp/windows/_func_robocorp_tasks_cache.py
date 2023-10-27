# If robocorp tasks is available, support feature to print
# screenshot on failure.
import typing
from typing import Iterator

# It's important that these imports are top-level as they should fail if
# robocorp-tasks is not there.
from robocorp.tasks import get_current_task, task_cache  # type:ignore

if typing.TYPE_CHECKING:
    from ._config import Config
    from ._desktop import Desktop


@task_cache
def config() -> "Config":
    """
    Internal API to create a config scoped based on the current task being run.
    """
    from ._config import Config

    return Config()


@task_cache
def desktop() -> Iterator["Desktop"]:
    """
    Internal API to create a desktop valid for the current task which will
    do a screenshot if an error happens.
    """
    from ._desktop import Desktop

    desktop = Desktop()
    yield desktop

    task = get_current_task()
    failed = False
    if task is not None:
        failed = task.failed

    screenshot_option = config().screenshot
    capture_screenshot = screenshot_option == "on" or (
        failed and screenshot_option == "only-on-failure"
    )
    if capture_screenshot:
        desktop.log_screenshot()
