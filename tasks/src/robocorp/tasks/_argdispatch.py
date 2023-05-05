from typing import List
from logging import getLogger

log = getLogger(__name__)


class _ArgDispatcher:
    def __init__(self):
        self._name_to_func = {}
        self.argparser = self._create_argparser()

    def _dispatch(self, parsed) -> int:
        if not parsed.command:
            self.argparser.print_help()
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

    def _create_argparser(self):
        import argparse

        parser = argparse.ArgumentParser(
            prog="robocorp.tasks",
            description="Robocorp framework for RPA development using Python.",
            epilog="View https://github.com/robocorp/robo for more information",
        )

        subparsers = parser.add_subparsers(dest="command")

        # Run
        run_parser = subparsers.add_parser(
            "run",
            help="run will collect tasks with the @task decorator and run the first that matches based on the task name filter.",
        )
        run_parser.add_argument(
            dest="path",
            help="The directory or file with the tasks to run.",
            nargs="?",
            default=".",
        )
        run_parser.add_argument(
            "-t",
            "--task",
            dest="task_name",
            help="The name of the task that should be run.",
            default="",
        )
        run_parser.add_argument(
            "-o",
            "--output-dir",
            dest="output_dir",
            help="The directory where the logging output files will be stored.",
            default="./output",
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

        return parser

    def process_args(self, args: List[str]) -> int:
        """
        Processes the arguments and return the returncode.
        """
        log.debug("Processing args: %s", " ".join(args))
        parser = self._create_argparser()
        try:
            parsed = parser.parse_args(args)
        except SystemExit as e:
            code = e.code
            if isinstance(code, int):
                return code
            if code is None:
                return 0
            return int(code)

        return self._dispatch(parsed)


arg_dispatch = _ArgDispatcher()
