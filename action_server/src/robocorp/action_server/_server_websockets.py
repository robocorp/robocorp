import asyncio
import logging
import typing
from dataclasses import asdict
from functools import partial
from typing import Any, Callable, Optional

if typing.TYPE_CHECKING:
    from fastapi.applications import FastAPI

    from ._models import Run
    from ._runs_state_cache import RunChangeEvent

log = logging.getLogger(__name__)


def include_websocket_socketio_routing(app: "FastAPI"):
    import socketio  # type: ignore

    sio_async_server = socketio.AsyncServer(
        async_mode="asgi",
        # Setting cors_allowed_origins="*" ends up putting
        # 'http://localhost:8085' in 'Access-Control-Allow-Origin'
        # which would end up giving an error such as:
        # 'Access-Control-Allow-Origin' header contains multiple values 'http://localhost:8085, *', but only one is allowed.
        # (because '*' is added by fastapi).
        # Setting [] makes it work properly and not add the additional 'Access-Control-Allow-Origin'
        # cors_allowed_origins="*",
        cors_allowed_origins=[],
        logger=log,
        engineio_logger=log,
    )
    ws_app = socketio.ASGIApp(socketio_server=sio_async_server, socketio_path="/api/ws")
    app.mount("/api/ws", ws_app)

    # A set with the client ids which are listening to runs
    clients_listening_runs = set()

    # List just to hold the callback called to notify that a change happened.
    on_run_change_callback: Optional[Callable[..., Any]] = None

    @sio_async_server.on("connect")
    async def handle_connect(sid, data):
        pass
        # print("Connected", sid)

    @sio_async_server.on("disconnect")
    async def handle_disconnect(sid):
        # print("Disconnected", sid)
        nonlocal on_run_change_callback

        from robocorp.action_server._runs_state_cache import get_global_runs_state

        global_runs_state = get_global_runs_state()

        with global_runs_state.semaphore:
            clients_listening_runs.discard(sid)
            await sio_async_server.leave_room(sid, room="run_listeners")
            if not clients_listening_runs:
                # No one listening: no need to listen for run changes
                if on_run_change_callback is not None:
                    global_runs_state.unregister(on_run_change_callback)
                    on_run_change_callback = None

    @sio_async_server.on("echo")
    async def handle_echo(sid, data):
        # Just echo something (testing)
        await sio_async_server.emit("echo", data)

    @sio_async_server.on("request")
    async def handle_request(sid, request_data):
        from starlette.concurrency import run_in_threadpool

        method = request_data.get("method")
        loop = asyncio.get_running_loop()
        if method == "GET":
            message_id = request_data.get("message_id")
            url = request_data.get("url")
            if url == "/api/actionPackages":

                async def _report_listed_actions(message: dict):
                    await sio_async_server.emit(
                        message["message_type"], message["data"], to=sid
                    )

                def on_listed_actions(message: dict):
                    asyncio.run_coroutine_threadsafe(
                        _report_listed_actions(message), loop
                    )

                loop.create_task(
                    run_in_threadpool(
                        partial(
                            _list_actions_in_threadpool,
                            on_listed_actions,
                            message_id,
                        )
                    )
                )

    @sio_async_server.on("start_listen_run_events")
    async def handle_start_listen_run_events(sid):
        from robocorp.action_server._runs_state_cache import get_global_runs_state

        nonlocal on_run_change_callback

        global_runs_state = get_global_runs_state()
        loop = asyncio.get_running_loop()

        with global_runs_state.semaphore:
            runs = global_runs_state.get_current_run_state()
            await _report_runs(sid, runs)
            if not clients_listening_runs:
                # Start listening if this is the first client added.
                if on_run_change_callback is None:
                    on_run_change_callback = partial(
                        _on_run_change_found_in_thread, loop
                    )
                    global_runs_state.register(on_run_change_callback)

            clients_listening_runs.add(sid)
            await sio_async_server.enter_room(sid, room="run_listeners")

    async def _report_runs(sid, runs: list["Run"]):
        await sio_async_server.emit(
            "runs_collected", {"runs": [asdict(run) for run in runs]}, to=sid
        )

    def _on_run_change_found_in_thread(loop, run_change_event: "RunChangeEvent"):
        """
        Note that this callback is called from a different thread.
        """
        asyncio.run_coroutine_threadsafe(_report_change_event(run_change_event), loop)

    async def _report_change_event(run_change_event: "RunChangeEvent"):
        try:
            if run_change_event.ev == "added":
                await sio_async_server.emit(
                    "run_added", {"run": asdict(run_change_event.run)}
                )
            elif run_change_event.ev == "changed":
                await sio_async_server.emit(
                    "run_changed",
                    {
                        "run_id": run_change_event.run.id,
                        "changes": run_change_event.changes,
                    },
                )
            else:
                log.critical(f"Unexpected run change event: {run_change_event}.")
        except Exception:
            log.exception("Error reporting change event to json.")


def _list_actions_in_threadpool(on_response_run_coroutine, message_id):
    from robocorp.action_server._api_action_package import list_action_packages

    try:
        action_packages = list_action_packages()
    except Exception:
        log.exception("Error collection action packages.")
        action_packages = []

    on_response_run_coroutine(
        {
            "message_type": "response",
            "data": {
                "message_id": message_id,
                "result": [asdict(p) for p in action_packages],
            },
        }
    )
