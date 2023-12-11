import asyncio
import logging
import os
import socket
import subprocess
import sys
from functools import partial
from pathlib import Path
from typing import Dict, Optional

log = logging.getLogger(__name__)

CURDIR = Path(__file__).parent.absolute()


def _name_as_summary(name):
    return name.replace("_", " ").title()


def _name_to_url(name):
    return name.replace("_", "-")


def start_server(expose: bool, api_key: str | None = None) -> None:
    import docstring_parser
    import uvicorn
    from fastapi.staticfiles import StaticFiles
    from starlette.requests import Request
    from starlette.responses import FileResponse, HTMLResponse

    from . import _actions_run
    from ._api_action_package import action_package_api_router
    from ._api_run import run_api_router
    from ._app import get_app
    from ._models import Action, ActionPackage, get_db
    from ._server_websockets import websocket_api_router
    from ._settings import get_settings

    settings = get_settings()

    log.debug("Starting server (settings: %s)", settings)

    app = get_app()

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
    app.include_router(websocket_api_router)

    @app.get("/base_log.html", response_class=HTMLResponse)
    async def serve_log_html(request: Request):
        from robocorp.log import _index_v3 as index

        return HTMLResponse(index.FILE_CONTENTS["index.html"])

    async def serve_index(request: Request):
        from ._static_contents import FILE_CONTENTS

        return HTMLResponse(FILE_CONTENTS["index.html"])

    index_routes = ["/", "/runs/{full_path:path}", "/actions/{full_path:path}"]
    for index_route in index_routes:
        app.add_api_route(
            index_route,
            serve_index,
            response_class=HTMLResponse,
            include_in_schema=False,
        )

    expose_subprocess = None

    def expose_later(loop):
        nonlocal expose_subprocess

        if not server.started:
            loop.call_later(1 / 15.0, partial(expose_later, loop))
            return

        port = settings.port if settings.port != 0 else None
        host = settings.address
        if port is None:
            sockets_ipv4 = [
                s for s in server.servers[0].sockets if s.family == socket.AF_INET
            ]
            if len(sockets_ipv4) == 0:
                raise Exception("Unable to find a port to expose")
            sockname = sockets_ipv4[0].getsockname()
            host = sockname[0]
            port = sockname[1]

        parent_pid = os.getpid()

        expose_subprocess = subprocess.Popen(
            [
                sys.executable,
                CURDIR / "_server_expose.py",
                str(parent_pid),
                str(port),
                "" if not settings.verbose else "v",
                host,
                settings.expose_url,
                str(api_key),
            ]
        )

    async def _on_startup():
        log.info("Documentation in /docs")
        if expose:
            loop = asyncio.get_event_loop()
            loop.call_later(1 / 15.0, partial(expose_later, loop))

    def _on_shutdown():
        from robocorp.action_server._robo_utils.process import (
            kill_process_and_subprocesses,
        )

        if expose_subprocess is not None:
            log.info("Shutting down expose subprocess: %s", expose_subprocess.pid)
            kill_process_and_subprocesses(expose_subprocess.pid)

    app.add_event_handler("startup", _on_startup)
    app.add_event_handler("shutdown", _on_shutdown)

    kwargs = settings.to_uvicorn()
    config = uvicorn.Config(app=app, **kwargs)
    server = uvicorn.Server(config)
    asyncio.run(server.serve())
