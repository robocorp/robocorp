import sys


def main(args=None, exit: bool = True) -> int:
    """Entry point for running actions from robocorp-actions."""

    # Note: robocorp-actions is almost only robocorp-tasks but with a few
    # different APIs.
    #
    # As both are under our control, we do some monkey-patching (hacking) of
    # internal stuff to get the API we want without changing robocorp-tasks too
    # much.

    from robocorp.tasks._argdispatch import _ArgDispatcher

    if args is None:
        args = sys.argv[1:]

    from robocorp.tasks import _constants
    from robocorp.tasks.cli import main

    _constants.DEFAULT_TASK_SEARCH_GLOB = "*action*.py|*task*.py"
    _constants.MODULE_ENTRY_POINT = "robocorp.actions"

    _ArgDispatcher._get_description = (  # type:ignore
        lambda self: "Robocorp Actions library"
    )

    def _add_task_argument(self, run_parser):
        run_parser.add_argument(
            "-a",
            "--action",
            dest="task_name",
            help="The name of the action that should be run.",
            action="append",
        )

    _ArgDispatcher._add_task_argument = _add_task_argument  # type:ignore

    def translate(msg):
        return (
            msg.replace("task", "action")
            .replace("Task", "Action")
            .replace("TASK", "ACTION")
        )

    def _get_argument_parser_class(self):
        import argparse

        class ArgumentParserTranslated(argparse.ArgumentParser):
            def format_usage(self):
                return translate(argparse.ArgumentParser.format_usage(self))

            def format_help(self):
                return translate(argparse.ArgumentParser.format_help(self))

        return ArgumentParserTranslated

    _ArgDispatcher._get_argument_parser_class = (  # type:ignore
        _get_argument_parser_class
    )

    return main(args, exit)
