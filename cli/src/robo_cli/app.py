import logging
import shutil
import subprocess
from pathlib import Path

import typer
from rich.console import Console, Group
from rich.logging import RichHandler
from rich.panel import Panel
from rich.prompt import IntPrompt, Prompt
from rich.table import Table

from robo_cli import core, environment, rcc, templates
from robo_cli.config import pyproject
from robo_cli.output import EndKeyword, StartKeyword
from robo_cli.process import ProcessError

app = typer.Typer(no_args_is_help=True)
console = Console(highlight=False)


def ensure_environment() -> dict[str, str]:
    try:
        with console.status("Building environment"):
            env = environment.ensure()
    except ProcessError as err:
        console.print(err.stderr)
        raise typer.Exit(code=1)

    env["RC_LOG_OUTPUT_STDOUT"] = "1"
    env["PYTHONUNBUFFERED"] = "1"
    return env


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

    ensure_environment()

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
    env = ensure_environment()

    with console.status("Parsing tasks"):
        try:
            tasks = core.list_tasks(env)
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


@app.command()
def run():
    """Runs the robot from current directory"""
    # TODO: Make global config object with effective values
    config = pyproject.load()

    # Empty output directory
    output_dir = Path(config.get("output", "output"))
    if output_dir.exists():
        shutil.rmtree(output_dir)
    output_dir.mkdir(parents=True)

    try:
        env = ensure_environment()

        with console.status("Parsing tasks"):
            try:
                tasks = core.list_tasks(env)
            except ProcessError as err:
                console.print(err.stderr)
                raise typer.Exit(code=1)

        taskname = tasks[0]["name"]
        stack = []

        def on_event(event):
            if isinstance(event, StartKeyword):
                console.print(f"{(len(stack) + 1) * '  '}{event.name}")
                stack.append(event)
            if isinstance(event, EndKeyword):
                stack.pop()

        with console.status(f"Running [bold]{taskname}[/bold]"):
            console.print()
            console.print("[bold]Start execution[/bold]")
            core.run_task(env, taskname, on_event)
            console.print()

    except ProcessError as exc:
        # TODO: Handle this through events instead of printing stderr
        console.print(exc.stderr)
        console.print("[bold red]Run failed due to unexpected error[/bold red]")
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


@app.command(
    context_settings={"allow_extra_args": True, "ignore_unknown_options": True}
)
def exec(ctx: typer.Context):
    """Run a command in the appropriate environment"""
    if not ctx.args:
        console.print("[bold red]No arguments given![/bold red]")
        raise typer.Exit(code=1)

    env = ensure_environment()

    try:
        console.print(f"[bold]{' '.join(ctx.args)}[/bold]")
        subprocess.run(ctx.args, env=env, check=True)
    except subprocess.CalledProcessError as err:
        raise typer.Exit(code=err.returncode)


@app.command()
def export():
    """Exports the robot from current directory to a zip file"""
    # TODO: Fix this
    with console.status("Exporting robot"):
        path = rcc.robot_wrap()

    console.print(f"Exported to {path}")
    console.print()


@app.command()
def deploy():
    """Deploys the robot from current directory to Control Room"""
    # TODO: Fix this
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
        f"Deploying to [underline]{workspace_url}/robots/{robot_id}/[/underline]"
    )

    # TODO: add an if to check for this. Currently this _only_ works for replacing
    # Confirm.ask("Project already exists, replace?")

    with console.status("Uploading project"):
        console.print(rcc.cloud_push(workspace_id, robot_id))

    console.print()
    console.print("Deploy of [bold]example[/bold] successful!")
    console.print(f"Link: [underline]{workspace_url}/robots/{robot_id}/[/underline]")
    console.print()


@app.callback()
def main(verbose: bool = False):
    level = "NOTSET" if verbose else "ERROR"
    logging.basicConfig(
        level=level,
        format="%(message)s",
        datefmt="[%X]",
        handlers=[RichHandler()],
    )


if __name__ == "__main__":
    app()
