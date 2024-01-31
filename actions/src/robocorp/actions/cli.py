import sys


def main(args=None, exit: bool = True) -> int:
    """Entry point for running actions from robocorp-actions."""
    from robocorp.actions._args_dispatcher import _ActionsArgDispatcher

    # Note: robocorp-actions is almost only robocorp-tasks but with a few
    # different APIs.
    #
    # As both are under our control, we rely on internal APIs to make
    # it seem to the external world as everything is action-based (and not
    # task-based).

    if args is None:
        args = sys.argv[1:]

    from robocorp.tasks import _constants
    from robocorp.tasks.cli import main

    _constants.DEFAULT_TASK_SEARCH_GLOB = "*action*.py|*task*.py"
    _constants.MODULE_ENTRY_POINT = "robocorp.actions"

    return main(args, exit, argument_dispatcher=_ActionsArgDispatcher())
