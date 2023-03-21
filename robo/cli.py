import typer

app = typer.Typer(no_args_is_help=True)


@app.command()
def na():
    # We need at least 2 commands with typer, otherwise it'll pass the command
    # as the first argument to the single command.
    raise RuntimeError("N/A")


@app.command()
def run(
    path: str = typer.Argument("."),
    task_name: str = typer.Argument(""),
    exit: bool = True,
):
    from robo._collect_tasks import Context, collect_tasks, Task
    from typing import Tuple

    context = Context()

    import sys
    from robo._exceptions import RoboCollectError
    from pathlib import Path

    if not task_name:
        context.show(f"\nCollecting tasks from: {path}")
    else:
        context.show(f"\nCollecting task {task_name} from: {path}")

    try:
        tasks: Tuple[Task, ...] = tuple(collect_tasks(Path(path), task_name))
    except RoboCollectError as e:
        context.show_error(str(e))
        if exit:
            sys.exit(1)
        return 1

    for task in tasks:
        task.run()


if __name__ == "__main__":
    # import sys
    # sys.argv.append('--help')
    app()
