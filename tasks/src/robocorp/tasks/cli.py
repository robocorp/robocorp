"""Main entry point for running tasks from robocorp-tasks.

Note that it's usually preferable to use `robocorp-tasks` as a command line
tool, using it programmatically through the main(args) in this module is also
possible.

Note: when running tasks, clients using this approach MUST make sure that any
code which must be automatically logged is not imported prior the the `cli.main`
call.
"""

import sys

# Use certificates from native storage
if sys.version_info >= (3, 10):
    import truststore

    truststore.inject_into_ssl()

# Just importing is enough to register the commands
from . import _commands  # @UnusedImport
from ._argdispatch import arg_dispatch as _arg_dispatch


def main(args=None, exit: bool = True) -> int:
    """Entry point for running tasks from robocorp-tasks."""
    if args is None:
        args = sys.argv[1:]

    returncode = _arg_dispatch.process_args(args)
    if exit:
        sys.exit(returncode)
    return returncode


if __name__ == "__main__":
    main()
