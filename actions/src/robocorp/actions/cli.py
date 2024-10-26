import sys
import typing
from typing import Optional

if typing.TYPE_CHECKING:
    # Don't add to public API here.
    from sema4ai_tasks._customization._plugin_manager import (
        PluginManager as _PluginManager,
    )


def main(
    args=None, exit: bool = True, plugin_manager: Optional["_PluginManager"] = None
) -> int:
    """
    Entry point for running actions from sema4ai-actions.

    Args:
        args: The command line arguments.

        exit: Determines if the process should exit right after executing the command.

        plugin_manager:
            Provides a way to customize internal functionality (should not
            be used by external clients in general).

    Returns:
        The exit code for the process.
    """
    from sema4ai.actions._args_dispatcher import _ActionsArgDispatcher

    # Note: sema4ai-actions is almost only sema4ai-tasks but with a few
    # different APIs.
    #
    # As both are under our control, we rely on internal APIs to make
    # it seem to the external world as everything is action-based (and not
    # task-based).

    if args is None:
        args = sys.argv[1:]

    from sema4ai_tasks import _constants
    from sema4ai_tasks.cli import main

    _constants.DEFAULT_TASK_SEARCH_GLOB = "*action*.py"
    _constants.MODULE_ENTRY_POINT = "sema4ai.actions"

    if plugin_manager is None:
        # If not provided, let's still add the 'request' as a managed parameter
        # (without any actual data).
        from sema4ai_tasks._customization._extension_points import EPManagedParameters
        from sema4ai_tasks._customization._plugin_manager import PluginManager

        from sema4ai.actions._managed_parameters import ManagedParameters
        from sema4ai.actions._request import Request

        plugin_manager = PluginManager()
        plugin_manager.set_instance(
            EPManagedParameters,
            ManagedParameters({"request": Request.model_validate({})}),
        )

    return main(
        args,
        exit,
        argument_dispatcher=_ActionsArgDispatcher(),
        plugin_manager=plugin_manager,
    )
