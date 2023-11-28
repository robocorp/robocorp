from logging import getLogger
from typing import List

from robocorp.tasks import _constants

log = getLogger(__name__)


class _ArgDispatcher:
    def __init__(self):
        self._name_to_func = {}

    def _dispatch(self, parsed) -> int:
        if not parsed.command:
            self._create_argparser().print_help()
            return 1

        method = self._name_to_func[parsed.command]
        dct = parsed.__dict__.copy()
        dct.pop("command")

        return method(**dct)

    def register(self, name=None):
        def do_register(func):
            nonlocal name
            if not name:
                name = func.__code__.co_name
            self._name_to_func[name] = func
            return func

        return do_register

    def _get_description(self):
        return "Robocorp framework for Python automations."

    def _add_task_argument(self, run_parser):
        run_parser.add_argument(
            "-t",
            "--task",
            dest="task_name",
            help="The name of the task that should be run.",
            action="append",
        )

    def _get_argument_parser_class(self):
        import argparse

        return argparse.ArgumentParser

    def _create_argparser(self):
        cls = self._get_argument_parser_class()
        parser = cls(
            prog=_constants.MODULE_ENTRY_POINT,
            description=self._get_description(),
            epilog="View https://github.com/robocorp/robo for more information",
        )

        subparsers = parser.add_subparsers(dest="command")

        # Run
        run_parser = subparsers.add_parser(
            "run",
            help="Collects tasks with the @task decorator and all tasks that matches based on the task name filter.",
        )
        run_parser.add_argument(
            dest="path",
            help="The directory or file with the tasks to run.",
            nargs="?",
            default=".",
        )
        run_parser.add_argument(
            "--glob",
            help="May be used to specify a glob to select from which files tasks should be searched (default '*task*.py')",
        )
        self._add_task_argument(run_parser)
        run_parser.add_argument(
            "-o",
            "--output-dir",
            dest="output_dir",
            help=(
                "The directory where the logging output files will be stored "
                "(default `ROBOT_ARTIFACTS` environment variable or `./output`)."
            ),
            default="",
        )
        run_parser.add_argument(
            "--max-log-files",
            dest="max_log_files",
            type=int,
            help="The maximum number of output files to store the logs.",
            default=5,
        )
        run_parser.add_argument(
            "--max-log-file-size",
            dest="max_log_file_size",
            help="The maximum size for the log files (i.e.: 1MB, 500kb).",
            default="1MB",
        )

        run_parser.add_argument(
            "--console-colors",
            help="""Define how the console messages shown should be color encoded.

"auto" (default) will color either using the windows API or the ansi color codes.
"plain" will disable console coloring.
"ansi" will force the console coloring to use ansi color codes.
""",
            dest="console_colors",
            type=str,
            choices=["auto", "plain", "ansi"],
            default="auto",
        )

        run_parser.add_argument(
            "--log-output-to-stdout",
            help="Can be used so that log messages are also sent to the 'stdout' (if not specified the RC_LOG_OUTPUT_STDOUT is also queried).",
            dest="log_output_to_stdout",
            type=str,
            choices=["no", "json"],
            default="",
        )

        run_parser.add_argument(
            "--preload-module",
            action="append",
            help="May be used to load a module(s) as the first step when collecting tasks.",
            dest="preload_module",
        )

        run_parser.add_argument(
            "--no-status-rc",
            help="When set, if running tasks has an error inside the task the return code of the process is 0.",
            dest="no_status_rc",
            action="store_true",
        )

        run_parser.add_argument(
            "--teardown-dump-threads-timeout",
            dest="teardown_dump_threads_timeout",
            type=float,
            help="The timeout (in seconds) to print running threads after the teardown starts (if not specified the RC_TEARDOWN_DUMP_THREADS_TIMEOUT is also queried). Defaults to 5 seconds.",
        )

        run_parser.add_argument(
            "--teardown-interrupt-timeout",
            dest="teardown_interrupt_timeout",
            type=float,
            help="The timeout (in seconds) to interrupt the teardown process  (if not specified the RC_TEARDOWN_INTERRUPT_TIMEOUT is also queried).",
        )

        run_parser.add_argument(
            "--os-exit",
            dest="os_exit",
            type=str,
            choices=["no", "before-teardown", "after-teardown"],
            help="Can be used to do an early os._exit to avoid the tasks session teardown or the interpreter teardown. Not recommended in general.",
        )

        # List tasks
        list_parser = subparsers.add_parser(
            "list",
            help="Provides output to stdout with json contents of the tasks available.",
        )
        list_parser.add_argument(
            dest="path",
            help="The directory or file from where the tasks should be listed (default is the current directory).",
            nargs="?",
            default=".",
        )
        list_parser.add_argument(
            "--glob",
            help=(
                "May be used to specify a glob to select from which files tasks should be searched (default '*task*.py')"
            ),
        )

        return parser

    def parse_args(self, args: List[str]):
        log.debug("Processing args: %s", " ".join(args))
        additional_args = []
        new_args = []
        for i, arg in enumerate(args):
            if arg == "--":
                # argparse.REMAINDER is buggy:
                # https://bugs.python.org/issue17050
                # So, remove '--' and everything after from what's passed to
                # argparser.
                additional_args.extend(args[i + 1 :])
                break
            new_args.append(arg)

        parser = self._create_argparser()
        parsed = parser.parse_args(new_args)

        if additional_args:
            parsed.additional_arguments = additional_args
        return parsed

    def process_args(self, args: List[str]) -> int:
        """
        Processes the arguments and return the returncode.
        """
        try:
            parsed = self.parse_args(args)
        except SystemExit as e:
            code = e.code
            if isinstance(code, int):
                return code
            if code is None:
                return 0
            return int(code)

        return self._dispatch(parsed)


arg_dispatch = _ArgDispatcher()
