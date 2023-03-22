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

    def register(self, func):
        self._name_to_func[func.__code__.co_name] = func
        return func

    def _create_argparser(self):
        import argparse

        parser = argparse.ArgumentParser(
            prog="robo",
            description="Robocorp framework for RPA development using Python.",
            # TODO: Add a proper epilog once we have an actual url to point to.
            # epilog="View https://github.com/robocorp/draft-python-framework/ for more information",
        )

        subparsers = parser.add_subparsers(dest="command")
        run_parser = subparsers.add_parser(
            "run",
            help="run will collect tasks with the @task decorator and run the first that matches based on the task name filter.",
        )
        run_parser.add_argument(
            dest="path",
            help="The directory or file with the tasks to run.",
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
