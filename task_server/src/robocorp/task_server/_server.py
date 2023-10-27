import logging
import sys
from pathlib import Path

import uvicorn
from fastapi.staticfiles import StaticFiles

from . import _database
from ._app import get_app
from ._runner import Runner
from ._process import ProcessError
from ._settings import get_settings
from ._tasks import Tasks
from ._watch import FileWatcher

LOGGER = logging.getLogger(__name__)


def start_server():
    settings = get_settings()
    tasks = Tasks.get_instance()
    runner = Runner.get_instance()

    LOGGER.debug("Starting server (settings: %s)", settings)

    def _on_change(paths: list[Path]):
        if settings.watch:
            LOGGER.info("Detected changes: %s", ", ".join(str(p) for p in paths))
            tasks.collect()

    watcher = FileWatcher(Path.cwd(), _on_change)

    def _on_startup():
        LOGGER.info(f"Documentation: http://{settings.address}:{settings.port}/docs")
        if settings.watch:
            watcher.start()

    def _on_shutdown():
        watcher.stop()

    app = get_app()
    app.add_event_handler("startup", _on_startup)
    app.add_event_handler("shutdown", _on_shutdown)

    runner.artifacts.mkdir(parents=True, exist_ok=True)
    app.mount(
        "/artifacts",
        StaticFiles(directory=runner.artifacts),
        name="artifacts",
    )
    app.mount(
        "/",
        StaticFiles(packages=[("robocorp.task_server", "_static")], html=True),
        name="static",
    )

    _database.ensure_tables()
    runner.load_history()
    
    try:
        tasks.collect()
    except ProcessError as err:
        logging.error("Failed to parse tasks:\n%s", err.stderr)
        sys.exit(1)

    kwargs = settings.to_uvicorn()
    uvicorn.run(app, **kwargs)
