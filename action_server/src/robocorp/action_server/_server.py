import asyncio
import logging
import os
import subprocess
import sys
from functools import partial
from pathlib import Path
from typing import Dict, Optional

import uvicorn
from fastapi.staticfiles import StaticFiles
from starlette.responses import FileResponse

log = logging.getLogger(__name__)

CURDIR = Path(__file__).parent.absolute()


def _name_as_summary(name):
    return name.replace("_", " ").title()


def _name_to_url(name):
    return name.replace("_", "-")


def start_server(expose: bool) -> None:
    import docstring_parser
    from starlette.requests import Request
    from starlette.responses import HTMLResponse

    from . import _actions_run
    from ._api_action_package import action_package_api_router
    from ._api_run import run_api_router
    from ._app import get_app
    from ._models import Action, ActionPackage, get_db
    from ._settings import get_settings

    settings = get_settings()

    log.debug("Starting server (settings: %s)", settings)

    app = get_app()

    app.add_event_handler("startup", _on_startup)
    app.add_event_handler("shutdown", _on_shutdown)

    artifacts_dir = settings.artifacts_dir

    app.mount(
        "/artifacts",
        StaticFiles(directory=artifacts_dir),
        name="artifacts",
    )

    db = get_db()
    action: Action
    action_package_id_to_action_package: Dict[str, ActionPackage] = dict(
        (action_package.id, action_package) for action_package in db.all(ActionPackage)
    )

    for action in db.all(Action):
        doc_desc: Optional[str] = ""
        if action.docs:
            try:
                parsed = docstring_parser.parse(action.docs)
                doc_desc = parsed.long_description or parsed.short_description
            except Exception:
                log.exception("Error parsing docstring: %s", action.docs)
                doc_desc = str(action.docs or "")

        if not doc_desc:
            doc_desc = ""

        action_package = action_package_id_to_action_package.get(
            action.action_package_id
        )
        if not action_package:
            log.critical("Unable to find action package: %s", action.action_package_id)
            continue

        app.add_api_route(
            f"/api/actions/{_name_to_url(action_package.name)}/{_name_to_url(action.name)}/run",
            _actions_run.generate_func_from_action(action),
            name=action.name,
            summary=_name_as_summary(action.name),
            description=doc_desc,
            operation_id=action.name,
            methods=["POST"],
        )

    app.include_router(run_api_router)
    app.include_router(action_package_api_router)

    async def serve_index(request: Request):
        return FileResponse(CURDIR / "_static" / "index.html")

    index_routes = ["/", "/runs/{full_path:path}", "/actions/{full_path:path}"]
    for index_route in index_routes:
        app.add_api_route(
            index_route,
            serve_index,
            response_class=HTMLResponse,
            include_in_schema=False,
        )

    def check_port(loop):
        if not server.started:
            loop.call_later(1 / 15.0, partial(check_port, loop))

        for s in server.servers:
            for socket in s.sockets:
                sock_name = socket.getsockname()
                # TODO: GET PORT HERE!
                print(sock_name)
        if expose:
            parent_pid = os.getpid()
            subprocess.Popen(
                [sys.executable, CURDIR / "_server_expose.py", str(parent_pid)]
            )

    async def _on_startup():
        log.info("Documentation in /docs")
        loop = asyncio.get_event_loop()
        loop.call_later(1 / 15.0, partial(check_port, loop))

    def _on_shutdown():
        pass

    app.add_event_handler("startup", _on_startup)
    app.add_event_handler("shutdown", _on_shutdown)

    kwargs = settings.to_uvicorn()
    config = uvicorn.Config(app=app, **kwargs)
    server = uvicorn.Server(config)
    asyncio.run(server.serve())
