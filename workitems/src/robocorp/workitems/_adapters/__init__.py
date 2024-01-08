import logging
import os

from robocorp.workitems._utils import import_by_name

from ._base import BaseAdapter
from ._file import FileAdapter
from ._robocorp import RobocorpAdapter

LOGGER = logging.getLogger(__name__)

GENERIC_MESSAGE = """\
Access to work items is only available from inside Control Room.
Using development-time simulated work items.

To learn more, see this guide: https://github.com/robocorp/robocorp/blob/master/workitems/docs/guides/local-development.md#using-a-custom-editor
To suppress this message, set the environment variable `RC_WORKITEM_ADAPTER`.
"""  # noqa

VSCODE_MESSAGE = """\
Access to work items is only available from inside Control Room.
To test different inputs and outputs, use the VSCode extension `Robocorp Code`.

To learn more, see this guide: https://robocorp.com/docs/development-guide/control-room/work-items#developing-with-work-items-locally
"""  # noqa


def create_adapter() -> BaseAdapter:
    """Resolve the correct API client/adapter to use based on the running
    environment.

    Unlike other Control Room features, such as Vault, it's not possible to
    access input/output work items outside of actual process runs. As such,
    we can assume that outside of those environments the user wants to use
    the file adapter. This should make setup easier and allow us to show
    better error messages.
    """
    adapter = os.getenv("RC_WORKITEM_ADAPTER") or os.getenv("RPA_WORKITEMS_ADAPTER")
    if adapter:
        return _import_adapter(adapter)
    else:
        return _detect_adapter()


def _import_adapter(name: str):
    # Backwards compatibility
    if name in ("FileAdapter", "RPA.Robocorp.WorkItems.FileAdapter"):
        return FileAdapter()

    klass = import_by_name(name, __name__)
    if not isinstance(klass, type) or not issubclass(klass, BaseAdapter):
        raise ValueError(f"Adapter '{klass}' does not inherit from BaseAdapter")

    return klass()


def _detect_adapter() -> BaseAdapter:
    # Should be an unattended run inside Control Room
    if _is_activity_run():
        return RobocorpAdapter()
    # The VSCode extension should set the adapter explicitly, which means
    # the user is not using the extension or the work items feature if we
    # reach this path
    elif _is_vscode_run():
        LOGGER.warning(VSCODE_MESSAGE)
        return FileAdapter()
    # Fallback to local development mode, might be configured correctly
    else:
        LOGGER.warning(GENERIC_MESSAGE)
        return FileAdapter()


def _is_vscode_run() -> bool:
    return bool(os.getenv("VSCODE_PID") or os.getenv("VSCODE_IPC_HOOK_CLI"))


def _is_activity_run() -> bool:
    return bool(
        os.getenv("RC_WORKSPACE_ID")
        and os.getenv("RC_PROCESS_RUN_ID")
        and os.getenv("RC_ACTIVITY_RUN_ID")
    )
