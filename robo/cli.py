from typing import Tuple
from pathlib import Path
import sys
from robo._argdispatch import arg_dispatch


def na():
    # We need at least 2 commands with typer, otherwise it'll pass the command
    # as the first argument to the single command.
    raise RuntimeError("N/A")


def _setup_log_output(output_dir: Path):
    import robocorp_logging

    # This can be called after user code is imported (but still prior to its
    # execution).
    return robocorp_logging.add_log_output(
        output_dir=output_dir,
        max_file_size="1MB",
        max_files=5,
        log_html=output_dir / "log.html",
    )


# Note: the args must match the 'dest' on the configured argparser.
@arg_dispatch.register
def run(
    output_dir: str,
    path: str,
    task_name: str,
):
    from robo._collect_tasks import collect_tasks
    from robo._hooks import before_task_run, after_task_run
    from robo._logging_setup import setup_auto_logging
    from robo._protocols import ITask
    from robo._task import Context
    from robo._protocols import Status

    p = Path(path)
    context = Context()
    if not p.exists():
        context.show_error(f"Path: {path} does not exist")
        return 1

    with setup_auto_logging(), _setup_log_output(Path(output_dir)):
        from robo._exceptions import RoboCollectError

        if not task_name:
            context.show(f"\nCollecting tasks from: {path}")
        else:
            context.show(f"\nCollecting task {task_name} from: {path}")

        try:
            tasks: Tuple[ITask, ...] = tuple(collect_tasks(p, task_name))
        except RoboCollectError as e:
            context.show_error(str(e))
            return 1

        if not tasks:
            context.show(f"Did not find any tasks in: {path}")
            return 1

        for task in tasks:
            before_task_run(task)
            try:
                task.run()
                task.status = Status.PASS
            except Exception as e:
                task.status = Status.ERROR
                task.message = str(e)
            finally:
                after_task_run(task)

            returncode = 0 if task.status == Status.PASS else 1
            return returncode


def main(args=None, exit: bool = True) -> int:
    if args is None:
        args = sys.argv[1:]
    returncode = arg_dispatch.process_args(args)
    if exit:
        sys.exit(returncode)
    return returncode


if __name__ == "__main__":
    main()
