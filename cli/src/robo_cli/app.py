import shutil
import subprocess
from pathlib import Path

import typer
from rich.console import Group
from rich.live import Live
from rich.panel import Panel
from rich.prompt import IntPrompt, Prompt
from rich.spinner import Spinner
from rich.table import Table

from robo_cli import environment, rcc, templates
from robo_cli.config import pyproject
from robo_cli.console import console
from robo_cli.core import commands
from robo_cli.core.builder import Builder, Model, Status, flatten_model
from robo_cli.process import ProcessError
from robo_cli.settings import get_settings

app = typer.Typer(no_args_is_help=True)


def ensure_environment() -> dict[str, str]:
    try:
        with console.status("Building environment"):
            env = environment.ensure()
    except ProcessError as err:
        console.print(err.stderr)
        raise typer.Exit(code=1)

    # Required for communicating with core framework
    env["RC_LOG_OUTPUT_STDOUT"] = "1"
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
            tasks = commands.list_tasks(env)
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
                tasks = commands.list_tasks(env)
            except ProcessError as err:
                console.print(err.stderr)
                raise typer.Exit(code=1)

        taskname = tasks[0]["name"]
        model = Model(name=taskname, status=Status.RUNNING, body=[])
        builder = Builder(model)

        console.print()
        with Live(refresh_per_second=30) as live:

            def on_event(event):
                builder.handle_event(event)

                spinner = Spinner("dots", f"Running [bold]{taskname}[/bold]")
                spinner_status = Spinner("dots")

                table = Table()
                table.add_column("Status")
                table.add_column("Name")

                flat = flatten_model(model)
                root, rows = flat[0], flat[1:]

                for name, status, depth in rows:
                    if status == Status.RUNNING:
                        status_icon = spinner_status
                    elif status == Status.ERROR:
                        status_icon = "🔴"
                    else:
                        status_icon = "🟢"
                    status_name = "  " * depth + name
                    table.add_row(status_icon, status_name)

                if root[1] == Status.RUNNING:
                    live.update(Group(table, spinner))
                else:
                    live.update(table)

            commands.run_task(env, taskname, on_event)
        console.print()

    except ProcessError:
        pass  # Errors are handled through output strewam

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
    settings = get_settings()
    settings.verbose = verbose
    console.is_debug = verbose


if __name__ == "__main__":
    app()
