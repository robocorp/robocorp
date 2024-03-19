import sys
import typing
from contextlib import contextmanager
from typing import Optional

from robocorp.tasks._argdispatch import _ArgDispatcher
from robocorp.tasks._customization._plugin_manager import PluginManager


def _translate(msg):
    return (
        msg.replace("task", "action")
        .replace("Task", "Action")
        .replace("TASK", "ACTION")
    )


class _ActionsArgDispatcher(_ArgDispatcher):
    def __init__(self, *args, **kwargs) -> None:
        super().__init__(*args, **kwargs)
        self.register("list")(self._list)
        self.register("run")(self._run)
        self._pm: Optional[PluginManager] = None

    @contextmanager
    def _register_lint(self, stream: typing.IO):
        from pathlib import Path

        from robocorp.tasks import _hooks

        from robocorp.actions import _lint_action
        from robocorp.actions._lint_action import format_lint_results

        files_found = set()

        def on_func_found(func, *args, **kwargs) -> None:
            import json

            from robocorp.actions._lint_action import (
                DiagnosticSeverity,
                DiagnosticsTypedDict,
                LintResultTypedDict,
            )

            filename = Path(func.__code__.co_filename).absolute()

            if filename not in files_found:
                files_found.add(filename)
                errors = list(
                    x.to_lsp_diagnostic()
                    for x in _lint_action.iter_lint_errors(
                        filename.read_bytes(), self._pm
                    )
                )
                if errors:
                    found_critical = False
                    error: DiagnosticsTypedDict
                    lint_result_contents: LintResultTypedDict = {
                        "file": str(filename),
                        "errors": errors,
                    }
                    lint_result = {"lint_result": lint_result_contents}

                    for error in errors:
                        if error["severity"] == DiagnosticSeverity.Error:
                            found_critical = True

                    if found_critical:
                        stream.write(json.dumps(lint_result))
                        stream.flush()
                        sys.exit(1)

                    # Critical not found: print to stderr
                    formatted = format_lint_results(lint_result_contents)
                    if formatted is not None:
                        sys.stderr.write(formatted.message)
                        sys.stderr.flush()

        with _hooks.on_task_func_found.register(on_func_found):
            yield

    def _list(self, *args, **kwargs):
        from contextlib import nullcontext, redirect_stdout

        from robocorp.tasks import _commands

        skip_lint = kwargs.pop("skip_lint", True)

        original_stdout = sys.stdout

        with redirect_stdout(sys.stderr):
            ctx = (
                self._register_lint(original_stdout) if not skip_lint else nullcontext()
            )
            with ctx:
                return _commands.list_tasks(*args, __stream__=original_stdout, **kwargs)

    def _run(self, *args, **kwargs):
        from robocorp.tasks import _commands

        return _commands.run(*args, **kwargs)

    def _get_description(self):
        return "Robocorp Actions library"

    def _add_task_argument(self, run_parser):
        run_parser.add_argument(
            "-a",
            "--action",
            dest="task_name",
            help="The name of the action that should be run.",
            action="append",
        )

    def _add_lint_argument(self, parser):
        parser.add_argument(
            "--skip-lint",
            dest="skip_lint",
            action="store_true",
            default=False,
            help="Skip `@action` linting when an action is found (by default any "
            "`@action` is linted for errors when found).",
        )

    def _create_run_parser(self, main_parser):
        parser = super()._create_run_parser(main_parser)
        # Not adding to run at this point.
        # self._add_lint_argument(parser)
        return parser

    def _create_list_tasks_parser(self, main_parser):
        parser = super()._create_list_tasks_parser(main_parser)
        self._add_lint_argument(parser)
        return parser

    def _get_argument_parser_class(self):
        import argparse

        class ArgumentParserTranslated(argparse.ArgumentParser):
            def format_usage(self):
                return _translate(argparse.ArgumentParser.format_usage(self))

            def format_help(self):
                return _translate(argparse.ArgumentParser.format_help(self))

        return ArgumentParserTranslated

    def _dispatch(self, parsed, pm: Optional[PluginManager] = None) -> int:
        # Custom dispatch as we need to account for custom flags.
        if not parsed.command:
            self._create_argparser().print_help()
            return 1

        method = self._name_to_func[parsed.command]
        dct = parsed.__dict__.copy()
        dct.pop("command")
        dct["pm"] = pm
        self._pm = pm

        return method(**dct)
