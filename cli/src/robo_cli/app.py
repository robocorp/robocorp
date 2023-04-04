import json
import shutil
import time
from pathlib import Path
from typing import List

import typer
from rich.console import Console, Group
from rich.panel import Panel
from rich.prompt import IntPrompt, Prompt
from rich.spinner import Spinner
from rich.table import Table

from robo_cli import environment, rcc, templates
from robo_cli.config import pyproject
from robo_cli.output import KIND_TO_EVENT, EndKeyword, StartKeyword
from robo_cli.process import Process, ProcessError

app = typer.Typer(no_args_is_help=True)
console = Console(highlight=False)


@app.command()
def new():
    """Creates a new project"""
    console.print()
    console.print("This command will guide you through creating your project")
    console.print()

    project_name = Prompt.ask("[cyan]Project name", default="example")
    project_root = Path(project_name)
    if project_root.exists():
        console.print(f"Project folder '{project_root}' already exists!")
        raise typer.Exit(code=1)

    choices = templates.list_templates()
    template = Prompt.ask(
        "[cyan]Project template",
        choices=choices,
        default="blank",
    )

    console.print()
    console.print("Initializing project")
    path = templates.copy_template(Path(project_name), template=template)

    with console.status("Building environment"):
        environment.ensure()

    console.print()
    console.print("✨ Project created ✨")
    console.print()
    console.print(f"Project path: {path.absolute()}")
    console.print()
    console.print("Configuration file: [bold]pyproject.toml[/bold]")
    console.print("Tasks file: [bold]tasks.py[/bold]")


@app.command()
def list():
    """List available tasks"""
    try:
        with console.status("Building environment"):
            env = environment.ensure()
            env["RC_LOG_OUTPUT_STDOUT"] = "1"
    except ProcessError as err:
        console.print(err.stderr)
        raise typer.Exit(code=1)

    with console.status("Parsing tasks"):
        proc = Process(
            [
                "python",
                "-m",
                "robo",
                "list",
                "tasks.py",
            ],
            env=env,
        )

        try:
            stdout, _ = proc.run()
            tasks = json.loads(stdout)
        except ProcessError as err:
            console.print(err.stderr)
            raise typer.Exit(code=1)

    if not tasks:
        console.print("No tasks defined!")
        raise typer.Exit(code=1)

    table = Table(title="Available tasks")
    table.add_column("Name", justify="right", style="cyan", no_wrap=True)
    table.add_column("Description")

    for task in tasks:
        table.add_row(task["name"], task["docs"])

    console.print()
    console.print(table)
    console.print()


def robot_run():
    spinner = Spinner("dots", "Running [bold]check-website[/bold]...")
    yield spinner

    time.sleep(2)

    steps = [
        "browser.open()",
        'browser.goto("http://robocorp.com")',
        "browser.take_screenshot()",
    ]

    status_spinner = Spinner("dots")

    for prog in range(len(steps)):
        table = Table()
        table.add_column("Status")
        table.add_column("Keyword")
        for idx in range(prog + 1):
            step = steps[idx]
            table.add_row("🟢" if idx < prog else status_spinner, step)

        yield Group(table, spinner)
        time.sleep(2)

    table = Table()
    table.add_column("Status")
    table.add_column("Keyword")
    for step in steps:
        table.add_row("🟢", step)

    yield table


@app.command()
def run():
    """Runs the robot from current directory"""
    # TODO: Make global config object with effective values
    config = pyproject.load()

    # Empty output directory
    output_dir = Path(config.get("output", "output"))
    if output_dir.exists():
        shutil.rmtree(output_dir)
    output_dir.mkdir()

    try:
        with console.status("Building environment"):
            env = environment.ensure()
            env["RC_LOG_OUTPUT_STDOUT"] = "1"

        with console.status("Parsing tasks"):
            proc = Process(
                [
                    "python",
                    "-m",
                    "robo",
                    "list",
                    "tasks.py",
                ],
                env=env,
            )

            try:
                stdout, _ = proc.run()
                tasks = json.loads(stdout)
            except ProcessError as err:
                console.print(err.stderr)
                raise typer.Exit(code=1)

        taskname = tasks[0]["name"]

        with console.status(f"Running [bold]{taskname}[/bold]"):
            env["RC_LOG_OUTPUT_STDOUT"] = "1"
            env["PYTHONUNBUFFERED"] = "1"

            # TODO: Figure out what to call from inner framework
            proc = Process(
                [
                    "python",
                    "-m",
                    "robo",
                    "run",
                    "tasks.py",
                    "-t",
                    taskname,
                ],
                env=env,
            )

            stack = []

            def handle_line(line: str):
                try:
                    payload = json.loads(line)
                    klass = KIND_TO_EVENT[payload["message_type"]]
                    event = klass.parse_obj(payload)
                    # console.print(event)
                    if isinstance(event, StartKeyword):
                        console.print(f"{(len(stack) + 1) * '  '}{event.name}")
                        stack.append(event)
                    if isinstance(event, EndKeyword):
                        stack.pop()
                except ValueError:
                    pass

            proc.on_stdout(handle_line)
            console.print()
            console.print("[bold]Start execution[/bold]")
            proc.run()
            console.print()

    except ProcessError as exc:
        print(exc.stderr)
        console.print("---")
        console.print("Run failed due to unexpected error")
        raise typer.Exit(code=1)

    artifacts = [str(name) for name in output_dir.glob("*")]
    console.print(
        Panel.fit(
            Group(*artifacts),
            title="Artifacts",
        )
    )

    console.print()
    console.print(f"Run [bold]{taskname}[/bold] successful!")
    console.print()


@app.command()
def export():
    """Exports the robot from current directory to a zip file"""
    console.print()
    with console.status("Exporting robot"):
        path = rcc.robot_wrap()

    console.print(f"Exported to {path}")
    console.print()


@app.command()
def deploy():
    """Deploys the robot from current directory to Control Room"""
    console.print()
    console.print()

    with console.status("Fetching workspace list"):
        workspaces = rcc.cloud_workspace()

    choices = {}
    console.print("Available workspaces:")
    for idx, key in enumerate(workspaces.keys(), 1):
        console.print(f"{idx}. {key}")
        choices[str(idx)] = key

    index = IntPrompt.ask("Workspace to deploy into?", choices=choices.keys())

    workspace = workspaces[choices[index]]
    workspace_id = workspace["id"]
    workspace_url = workspace["url"]

    # TODO: have option to select from list of robot ids or create new one
    robot_id = Prompt.ask("Robot id to deploy with?", default="example")

    console.print(
        "Deploying [bold]example[/bold] to "
        + f"[underline]{workspace_url}/robots/{robot_id}/[/underline]"
    )
    console.print()

    # TODO: add an if to check for this. Currently this _only_ works for replacing
    # Confirm.ask("Project already exists, replace?")

    with console.status("Uploading project"):
        console.print(rcc.cloud_push(workspace_id, robot_id))

    console.print()
    console.print("Deploy of [bold]example[/bold] successful!")
    console.print(f"Link: [underline]{workspace_url}/robots/{robot_id}/[/underline]")
    console.print()


def _run(env, args: List[str]):
    assert len(args) > 0, "Must provide at least one argument"
    try:
        proc = Process(args=args, env=env)

        try:
            stdout, stderr = proc.run()
            # TODO: do we want to let black / ruff stdouts through?
            # if stdout:
            #     console.print(stdout)
            # if stderr:
            #     console.print(stderr)
        except ProcessError as err:
            console.print(f"Fail during {args[0]}")
            console.print(err.stdout)
            console.print(err.stderr)
            raise typer.Exit(code=1)
    except ProcessError as exc:
        print(exc.stderr)
        console.print("---")
        console.print("Linting failed due to unexpected error")
        raise typer.Exit(code=1)


@app.command()
def lint(fix: bool = typer.Option(False, "--fix", "-f")):
    """Runs linting and formatting on the project"""

    # TODO: generate ruff settings into the pyproject.toml
    #
    #    [tool.ruff]
    #    # TODO: We should generate this inside the hood
    #    target-version = "py39"

    try:
        with console.status("Building environment"):
            env = environment.ensure_devdeps()
    except ProcessError as err:
        console.print("Error building linting environment")
        console.print(err.stderr)
        raise typer.Exit(code=1)

    ruff_command = ["ruff", "check", "tasks.py"]
    black_command = ["python", "-m", "black", "tasks.py"]

    if fix:
        ruff_command.insert(2, "--fix")
        black_command.insert(3, "--check")

    console.print()
    with console.status("Linting and formatting"):
        _run(env, ruff_command)
        _run(env, black_command)
    console.print("Linting and formatting succesful!")
    console.print()


if __name__ == "__main__":
    app()
