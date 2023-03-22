import typer
from typing import Tuple
from pathlib import Path

app = typer.Typer(no_args_is_help=True)


@app.command()
def na():
    # We need at least 2 commands with typer, otherwise it'll pass the command
    # as the first argument to the single command.
    raise RuntimeError("N/A")


def _setup_log_output(output_dir):
    import robocorp_logging

    # This can be called after user code is imported (but still prior to its
    # execution).
    return robocorp_logging.add_log_output(
        output_dir=output_dir,
        max_file_size="1MB",
        max_files=5,
        log_html=output_dir / "log.html",
    )


@app.command()
def run(
    path: str = typer.Argument("."),
    task_name: str = typer.Argument(""),
    exit: bool = True,
):
    from robo._collect_tasks import collect_tasks
    from robo._hooks import before_task_run, after_task_run
    from robo._logging_setup import setup_auto_logging
    from robo._protocols import ITask
    from robo._task import Context
    from robo._protocols import Status

    with setup_auto_logging(), _setup_log_output(Path(path) / "output"):
        context = Context()

        import sys
        from robo._exceptions import RoboCollectError

        if not task_name:
            context.show(f"\nCollecting tasks from: {path}")
        else:
            context.show(f"\nCollecting task {task_name} from: {path}")

        try:
            tasks: Tuple[ITask, ...] = tuple(collect_tasks(Path(path), task_name))
        except RoboCollectError as e:
            context.show_error(str(e))
            if exit:
                sys.exit(1)
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


if __name__ == "__main__":
    # import sys
    # sys.argv.append('--help')
    app()
