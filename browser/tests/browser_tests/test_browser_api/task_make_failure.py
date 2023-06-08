from pathlib import Path

from robocorp.tasks import task

from robocorp.browser import goto


@task
def use_browser_and_fail() -> None:
    page1_html: Path = Path(__file__).absolute().parent / "page1.html"
    goto(page1_html.as_uri())
    raise RuntimeError("Some error...")
