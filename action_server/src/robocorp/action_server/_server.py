import asyncio
import logging
import os
import socket
import subprocess
import sys
from functools import partial
from typing import Dict, Optional, Sequence

from termcolor import colored

from ._protocols import IBeforeStartCallback

log = logging.getLogger(__name__)


def _name_as_summary(name):
    return name.replace("_", " ").title()


def _name_to_url(name):
    from robocorp.action_server._slugify import slugify

    return slugify(name.replace("_", "-"))


def build_url_api_run(action_package_name: str, action_name: str) -> str:
    return f"/api/actions/{_name_to_url(action_package_name)}/{_name_to_url(action_name)}/run"


def get_action_description_from_docs(docs: str) -> str:
    import docstring_parser

    doc_desc: str
    try:
        parsed = docstring_parser.parse(docs)
        if parsed.short_description and parsed.long_description:
            doc_desc = f"{parsed.short_description}\n{parsed.long_description}"
        else:
            doc_desc = parsed.long_description or parsed.short_description or ""
    except Exception:
        log.exception("Error parsing docstring: %s", docs)
        doc_desc = str(docs or "")
    return doc_desc


def start_server(
    expose: bool,
    api_key: str | None,
    expose_session: str | None,
    whitelist: str | None,
    before_start: Sequence[IBeforeStartCallback],
) -> None:
    from dataclasses import asdict

    import uvicorn
    from fastapi import Depends, HTTPException, Security
    from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
    from fastapi.staticfiles import StaticFiles
    from starlette.requests import Request
    from starlette.responses import HTMLResponse

    from . import _actions_process_pool, _actions_run
    from ._api_action_package import action_package_api_router
    from ._api_run import run_api_router
    from ._app import get_app
    from ._models import Action, ActionPackage, get_db
    from ._server_websockets import websocket_api_router
    from ._settings import get_settings

    settings = get_settings()

    settings_dict = asdict(settings)
    settings_str = "\n".join(f"    {k} = {v!r}" for k, v in settings_dict.items())
    log.debug(f"Starting server. Settings:\n{settings_str}")

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

    def verify_api_key(
        token: HTTPAuthorizationCredentials = Security(HTTPBearer(auto_error=True)),
    ) -> HTTPAuthorizationCredentials:
        if token.credentials != api_key:
            raise HTTPException(
                status_code=403,
                detail="Invalid or missing API Key",
            )
        else:
            return token

    endpoint_dependencies = []

    if api_key:
        endpoint_dependencies.append(Depends(verify_api_key))

    actions = db.all(Action)
    for action in actions:
        if not action.enabled:
            # Disabled actions should not be registered.
            continue

        doc_desc: Optional[str] = ""
        if action.docs:
            doc_desc = get_action_description_from_docs(action.docs)

        if not doc_desc:
            doc_desc = ""

        action_package = action_package_id_to_action_package.get(
            action.action_package_id
        )
        if not action_package:
            log.critical("Unable to find action package: %s", action.action_package_id)
            continue

        if whitelist:
            from ._whitelist import accept_action

            if not accept_action(whitelist, action_package.name, action.name):
                log.info(
                    "Skipping action %s / %s (not in whitelist)",
                    action_package.name,
                    action.name,
                )
                continue

        func, openapi_extra = _actions_run.generate_func_from_action(action)
        if action.is_consequential is not None:
            openapi_extra["x-openai-isConsequential"] = action.is_consequential

        app.add_api_route(
            build_url_api_run(action_package.name, action.name),
            func,
            name=action.name,
            summary=_name_as_summary(action.name),
            description=doc_desc,
            operation_id=action.name,
            methods=["POST"],
            dependencies=endpoint_dependencies,
            openapi_extra=openapi_extra,
        )

    if os.getenv("RC_ADD_SHUTDOWN_API", "").lower() in ("1", "true"):

        def shutdown(timeout: int = -1):
            import _thread
            import time

            from robocorp.action_server._robo_utils.run_in_thread import run_in_thread

            _thread.interrupt_main()

            def interrupt_again():
                time.sleep(timeout)
                _thread.interrupt_main()

            if timeout > 0:
                run_in_thread(interrupt_again, daemon=True)

        app.add_api_route("/api/shutdown/", shutdown, methods=["POST"])

    app.include_router(run_api_router, include_in_schema=settings.full_openapi_spec)
    app.include_router(
        action_package_api_router, include_in_schema=settings.full_openapi_spec
    )
    app.include_router(websocket_api_router)

    @app.get("/config", include_in_schema=settings.full_openapi_spec)
    async def serve_config():
        from ._server_expose import get_expose_session_payload, read_expose_session_json

        payload = {"expose_url": False, "auth_enabled": False}

        if api_key:
            payload["auth_enabled"] = True

        if expose:
            current_expose_session = read_expose_session_json(
                datadir=str(settings.datadir)
            )

            expose_session_payload = (
                get_expose_session_payload(current_expose_session.expose_session)
                if current_expose_session
                else None
            )

            if expose_session_payload:
                payload[
                    "expose_url"
                ] = f"https://{expose_session_payload.sessionId}.{settings.expose_url}"

        return payload

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
            include_in_schema=settings.full_openapi_spec,
        )

    # At this point the FastAPI app should be configured. What's missing now
    # is setup callbacks related to the startup and actuall start the async
    # loop.

    for callback in before_start:
        if not callback(app):
            return

    expose_subprocess = None

    def _get_currrent_host():
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

        return (host, port)

    def expose_later(loop):
        from robocorp.action_server._settings import is_frozen

        nonlocal expose_subprocess

        if not server.started:
            loop.call_later(1 / 15.0, partial(expose_later, loop))
            return

        (host, port) = _get_currrent_host()

        parent_pid = os.getpid()

        if is_frozen():
            # The executable is 'action-server.exe'.
            args = [sys.executable]
        else:
            # The executable is 'python'.
            args = [
                sys.executable,
                "-m",
                "robocorp.action_server",
            ]

        args += [
            "server-expose",
            str(parent_pid),
            str(port),
            "" if not settings.verbose else "v",
            host,
            settings.expose_url,
            settings.datadir,
            str(expose_session),
            api_key,
        ]
        expose_subprocess = subprocess.Popen(args)

    def _on_started_message(self, **kwargs):
        (host, port) = _get_currrent_host()

        log.info(
            colored("\n  ⚡️ Local Action Server: ", "green", attrs=["bold"])
            + colored(f"http://{settings.address}:{port}", "light_blue")
        )

        if not expose:
            log.info(
                colored("     Public access: use ", attrs=["dark"])
                + colored("--expose", attrs=["bold"])
                + colored(" to expose\n", attrs=["dark"])
            )

            if api_key:
                log.info(
                    colored("  🔑 API Authorization Bearer key: ", attrs=["bold"])
                    + f"{api_key}\n"
                )

    async def _on_startup():
        if expose:
            loop = asyncio.get_event_loop()
            loop.call_later(1 / 15.0, partial(expose_later, loop))

    def _on_shutdown():
        import psutil

        log.info("Stopping action server...")
        from robocorp.action_server._robo_utils.process import (
            kill_process_and_subprocesses,
        )

        expose_pid = None
        if expose_subprocess is not None:
            log.info("Shutting down expose subprocess: %s", expose_subprocess.pid)
            expose_pid = expose_subprocess.pid
            kill_process_and_subprocesses(expose_pid)

        p = psutil.Process(os.getpid())
        try:
            children_processes = list(p.children(recursive=True))
        except Exception:
            log.exception("Error listing subprocesses.")

        for child in children_processes:
            if child.pid != expose_pid:  # If it's still around, don't kill it again.
                log.info("Killing sub-process when exiting action server: %s", child)
                try:
                    kill_process_and_subprocesses(child.pid)
                except Exception:
                    log.exception("Error killing subprocess: %s", child.pid)

    app.add_event_handler("startup", _on_startup)
    app.add_event_handler("shutdown", _on_shutdown)

    with _actions_process_pool.setup_actions_process_pool(
        settings, action_package_id_to_action_package, actions
    ):
        kwargs = settings.to_uvicorn()
        config = uvicorn.Config(app=app, **kwargs)
        server = uvicorn.Server(config)
        server._log_started_message = _on_started_message  # type: ignore[assignment]

        asyncio.run(server.serve())
