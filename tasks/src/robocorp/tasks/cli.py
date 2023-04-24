from pathlib import Path
from typing import Tuple

import json
import os
import sys
import traceback

from ._argdispatch import arg_dispatch


# Note: the args must match the 'dest' on the configured argparser.
@arg_dispatch.register(name="list")
def list_tasks(
    path: str,
) -> int:
    """
    Prints the tasks available at a given path to the stdout in json format.

    [
        {
            "name": "task_name",
            "line": 10,
            "file": "/usr/code/projects/tasks.py",
            "docs": "Task docstring",
        },
        ...
    ]

    Args:
        path: The path (file or directory) from where tasks should be collected.
    """
    from robocorp.tasks._collect_tasks import collect_tasks
    from robocorp.tasks._task import Context
    from robocorp.tasks._protocols import ITask

    p = Path(path)
    context = Context()
    if not p.exists():
        context.show_error(f"Path: {path} does not exist")
        return 1

    task: ITask
    tasks_found = []
    for task in collect_tasks(p):
        tasks_found.append(
            {
                "name": task.name,
                "line": task.lineno,
                "file": task.filename,
                "docs": getattr(task.method, "__doc__") or "",
            }
        )

    sys.stdout.write(json.dumps(tasks_found))
    return 0


# Note: the args must match the 'dest' on the configured argparser.
@arg_dispatch.register()
def run(
    output_dir: str,
    path: str,
    task_name: str,
    max_log_files: int = 5,
    max_log_file_size: str = "1MB",
) -> int:
    """
    Runs a task.

    Args:
        output_dir: The directory where output should be put.
        path: The path (file or directory where the tasks should be collected from.
        task_name: The name of the task to run.
        max_log_files: The maximum number of log files to be created (if more would
            be needed the oldest one is deleted).
        max_log_file_size: The maximum size for the created log files.

    Returns:
        0 if everything went well.
        1 if there was some error running the task.
    """
    from ._collect_tasks import collect_tasks
    from ._hooks import before_task_run, after_task_run
    from ._protocols import ITask
    from ._task import Context
    from ._protocols import Status
    from ._exceptions import RoboCollectError
    from ._log_auto_setup import (
        setup_cli_auto_logging,
        read_filters_from_pyproject_toml,
    )
    from ._log_output_setup import setup_log_output, setup_stdout_logging

    # Don't show internal machinery on tracebacks:
    # setting __tracebackhide__ will make it so that robocorp-log
    # won't show this frame onwards in the logging.
    __tracebackhide__ = 1

    p = Path(path).absolute()
    context = Context()
    if not p.exists():
        context.show_error(f"Path: {path} does not exist")
        return 1

    from robocorp import log

    config = read_filters_from_pyproject_toml(context, p)

    with setup_cli_auto_logging(
        # Note: we can't customize what's a "project" file or a "library" file, right now
        # the customizations are all based on module names.
        config
    ), setup_stdout_logging(), setup_log_output(
        output_dir=Path(output_dir),
        max_files=max_log_files,
        max_file_size=max_log_file_size,
    ):
        run_status = "PASS"
        setup_message = ""

        run_name = f"{os.path.basename(path)} - {task_name}"
        log.start_run(run_name)

        try:
            log.start_task("Collect tasks", "setup", "", 0)
            try:
                if not task_name:
                    context.show(f"\nCollecting tasks from: {path}")
                else:
                    context.show(f"\nCollecting task {task_name} from: {path}")

                tasks: Tuple[ITask, ...] = tuple(collect_tasks(p, task_name))

                if not tasks:
                    raise RoboCollectError(f"Did not find any tasks in: {path}")
                if len(tasks) > 1:
                    raise RoboCollectError(
                        f"Expected only 1 task to be run. Found: {', '.join(t.name for t in tasks)}"
                    )
            except Exception as e:
                run_status = "ERROR"
                setup_message = str(e)
                log.exception()

                if not isinstance(e, RoboCollectError):
                    traceback.print_exc()
                else:
                    context.show_error(setup_message)

                return 1
            finally:
                log.end_task("Collect tasks", "setup", run_status, setup_message)

            for task in tasks:
                before_task_run(task)
                try:
                    task.run()
                    run_status = task.status = Status.PASS
                except Exception as e:
                    run_status = task.status = Status.ERROR
                    task.message = str(e)
                finally:
                    after_task_run(task)

                returncode = 0 if task.status == Status.PASS else 1
                return returncode

            raise AssertionError("Should never get here.")
        finally:
            log.end_run(run_name, run_status)


def main(args=None, exit: bool = True) -> int:
    if args is None:
        args = sys.argv[1:]
    returncode = arg_dispatch.process_args(args)
    if exit:
        sys.exit(returncode)
    return returncode


if __name__ == "__main__":
    main()
