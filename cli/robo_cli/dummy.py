# A dummy cli showcasing rich and typer.
import time

import typer
from rich.console import Console, Group
from rich.live import Live
from rich.panel import Panel
from rich.progress import Progress
from rich.prompt import Prompt, Confirm
from rich.spinner import Spinner
from rich.table import Table
from rich.text import Text

app = typer.Typer(no_args_is_help=True)

console = Console()


@app.command()
def dummy_new():
    console.print()
    console.print("This command will guide you through creating your project")
    console.print()

    Prompt.ask("[cyan]Project name", default="example")
    Prompt.ask(
        "[cyan]Project template",
        choices=["blank", "browser", "desktop"],
        default="blank",
    )

    console.print()
    console.print("Initializing project (digest: d4dc98983ae5f86e)")
    with Progress() as progress:

        def run_task(name, size):
            task = progress.add_task(name, total=size)
            for _ in range(size):
                progress.update(task, advance=1)
                time.sleep(0.01)

        run_task("[red] Downloading", 200)
        run_task("[cyan] Installing ", 300)
        run_task("[green] Finalizing", 100)

    console.print()
    console.print("✨ Project created ✨")
    console.print()
    console.print("Configuration file: [bold]pyproject.toml[/bold]")
    console.print("Tasks file: [bold]tasks.py[/bold]")


def dummy_robot_run():
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
def dummy_run():
    print("run")
    with Live(refresh_per_second=30) as live:
        for step in dummy_robot_run():
            live.update(step)

    console.print(
        Panel.fit(
            Group("[bold]log.html[/bold]", "browser-screenshot-1.png"),
            title="Artifacts",
        )
    )

    console.print()
    console.print("Run [bold]check-website[/bold] successful!")
    console.print()


@app.command()
def dummy_deploy():
    console.print()
    console.print(
        "Deploying [bold]example[/bold] to [underline]https://cloud.robocorp.com/organization/example/[/underline]"
    )
    console.print()

    Confirm.ask("Project already exists, replace?")

    with console.status("Uploading project"):
        time.sleep(3)

    console.print()
    console.print("Deploy of [bold]example[/bold] successful!")
    console.print(
        "Link: [underline]https://cloud.robocorp.com/organization/example/robots/example[/underline]"
    )
    console.print()


@app.command()
def dummy_list():
    console.print()
    console.print("> robo run")

    desc = Text.assemble("\nTasks for handling generated report files\n")

    table = Table(title="Tasks")
    table.add_column("ID")
    table.add_column("Name", justify="right", style="cyan", no_wrap=True)
    table.add_column("Description")

    table.add_row("1", "copy-reports", "Copy reports to output")
    table.add_row("2", "remove-reports", "Remove generated reports")

    console.print()
    console.print(Panel.fit(Group(desc, table), title="example"))
    console.print()
    Prompt.ask("Select task to run", choices=["1", "2"])
    console.print()
