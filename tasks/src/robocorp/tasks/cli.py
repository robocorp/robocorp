# ruff: noqa: E402
"""Main entry point for running tasks from robocorp-tasks.

Note that it's usually preferable to use `robocorp-tasks` as a command line
tool, using it programmatically through the main(args) in this module is also
possible.

Note: when running tasks, clients using this approach MUST make sure that any
code which must be automatically logged is not imported prior the the `cli.main`
call.
"""

import sys
from typing import List, Optional, Protocol

# Use certificates from native storage (if `truststore` installed)
if sys.version_info >= (3, 10):
    try:
        import truststore  # type: ignore

        truststore.inject_into_ssl()
    except ModuleNotFoundError:
        pass

if sys.platform == "win32":
    # Apply workaround where `asyncio` would halt forever when windows UIAutomation.dll
    # is used with comtypes.
    # see: https://github.com/python/cpython/issues/111604
    _COINIT_MULTITHREADED = 0x0
    sys.coinit_flags = _COINIT_MULTITHREADED  # type:ignore

# Just importing is enough to register the commands
from . import _commands  # noqa


class IArgumentsHandler(Protocol):
    def process_args(self, args: List[str]) -> int:
        """
        Args:
            args: The arguments to process.

        Returns: the exitcode.
        """


def main(
    args=None,
    exit: bool = True,
    argument_dispatcher: Optional[IArgumentsHandler] = None,
) -> int:
    """Entry point for running tasks from robocorp-tasks."""
    if args is None:
        args = sys.argv[1:]

    dispatcher: IArgumentsHandler
    if argument_dispatcher is None:
        from ._argdispatch import arg_dispatch as dispatcher
    else:
        dispatcher = argument_dispatcher

    returncode = dispatcher.process_args(args)
    if exit:
        sys.exit(returncode)
    return returncode


if __name__ == "__main__":
    main()
