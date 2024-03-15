# ruff: noqa: E402
"""Main entry point for running tasks from robocorp-tasks.

Note that it's usually preferable to use `robocorp-tasks` as a command line
tool, using it programmatically through the main(args) in this module is also
possible.

Note: when running tasks, clients using this approach MUST make sure that any
code which must be automatically logged is not imported prior the the `cli.main`
call.
"""
import os
import sys
import typing
import warnings
from typing import List, Optional, Protocol

if typing.TYPE_CHECKING:
    # i.e.: Don't add to public API.
    from ._customization._plugin_manager import PluginManager as _PluginManager


def inject_truststore():
    # Use certificates from native storage (if `truststore` installed)

    # _RC_TEST_USE_TRUSTSTORE env var is only used to avoid unwanted warnings in tests
    # and should not be used for other purposes
    if os.getenv("_RC_TEST_USE_TRUSTSTORE", "True").lower() in ["false", "0"]:
        return

    if sys.version_info >= (3, 10):
        try:
            import truststore  # type: ignore

            truststore.inject_into_ssl()
        except ModuleNotFoundError:
            warnings.warn(
                "Usage of the native system certificate stores can’t be enabled, ensure you have the"
                " `robocorp-truststore` dependency installed in the environment.",
                Warning,
                stacklevel=2,
            )


inject_truststore()

if sys.platform == "win32":
    # Apply workaround where `asyncio` would halt forever when windows UIAutomation.dll
    # is used with comtypes.
    # see: https://github.com/python/cpython/issues/111604
    _COINIT_MULTITHREADED = 0x0
    sys.coinit_flags = _COINIT_MULTITHREADED  # type:ignore

# Just importing is enough to register the commands
from . import _commands  # noqa


class IArgumentsHandler(Protocol):
    def process_args(
        self, args: List[str], pm: Optional["_PluginManager"] = None
    ) -> int:
        """
        Args:
            args: The arguments to process.
            pm: The plugin manager used to customize internal functionality.

        Returns: the exitcode.
        """


def main(
    args=None,
    exit: bool = True,
    argument_dispatcher: Optional[IArgumentsHandler] = None,
    plugin_manager: Optional["_PluginManager"] = None,
) -> int:
    """
    Entry point for running tasks from robocorp-tasks.

    Args:
        args: The command line arguments.

        exit: Determines if the process should exit right after executing the command.

        plugin_manager:
            Provides a way to customize internal functionality (should not
            be used by external clients in general).

    Returns:
        The exit code for the process.
    """
    if args is None:
        args = sys.argv[1:]

    dispatcher: IArgumentsHandler
    if argument_dispatcher is None:
        from ._argdispatch import arg_dispatch as dispatcher
    else:
        dispatcher = argument_dispatcher

    returncode = dispatcher.process_args(args, pm=plugin_manager)
    if exit:
        sys.exit(returncode)
    return returncode


if __name__ == "__main__":
    main()
