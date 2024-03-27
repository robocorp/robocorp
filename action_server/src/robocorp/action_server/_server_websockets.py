import asyncio
import itertools
import logging
import typing
from dataclasses import asdict
from functools import partial
from typing import Any, Callable, Dict, Optional, Sequence, Set

from fastapi.routing import APIRouter
from starlette.websockets import WebSocket, WebSocketDisconnect

if typing.TYPE_CHECKING:
    from ._models import Run
    from ._runs_state_cache import RunChangeEvent

log = logging.getLogger(__name__)

websocket_api_router = APIRouter(prefix="/api/ws")


class SocketServer:
    """
    Websocket acting as a server with a socket.io-like API.

    Note: trying to integrate socket.io directly had issues (where the
    connections wouldn't always properly connect) and it was hard to diagnose
    why that happened, so a custom implementation was rolled out in this
    class which just uses a plain websocket managed by FastAPI with the API
    being inspired by socket.io.

    The basic usage is:

    ```
    socket_server = SocketServer()

    # Configure all method handlers based on events
    # (handlers receive the socket id which can be used
    # to talk to just that client).
    @socket_server.on("connect")
    async def handle_connect(sid: str):
        print("Connected", sid)


    # When a websocket connection is done register it in
    # the socket server.

    await ws.accept()
    await socket_server.manage_websocket(ws)
    ```
    """

    def __init__(self) -> None:
        self.event_handlers: dict = {}
        self._rooms: Dict[str, Set[str]] = {}

        # List just to hold the callback called to notify that a change happened.
        self.on_run_change_callback: Optional[Callable[..., Any]] = None
        self._next_id = partial(next, itertools.count(0))
        self._sid_to_websocket: Dict[str, WebSocket] = {}

    def enter_room(self, sid: str, room: str) -> None:
        """
        Adds an sid to a room.
        """
        self._rooms.setdefault(room, set()).add(sid)

    def leave_room(self, sid: str, room: str) -> None:
        """
        Removes an sid from a room.
        """
        sids_in_room = self._rooms.get(room)
        if sids_in_room:
            sids_in_room.discard(sid)

    def get_room_sids(self, room: str) -> Optional[Set[str]]:
        """
        Gets the sids that are in a room.

        Note: the returned set should not be mutated.
        """
        return self._rooms.get(room)

    def on(self, event_name: str):
        """
        Registers a handler function for a specific event.
        """

        def register(func):
            self.event_handlers.setdefault(event_name, []).append(func)
            return func

        return register

    def _gen_id(self) -> str:
        """
        Generates an identifier used to identify a connection.
        """
        return f"client-{self._next_id()}"

    async def emit(
        self, event: str, data=None, *, to: Optional[str | Sequence[str]] = None
    ):
        """
        Emits an event which is sent to the user.

        Args:
            to: The client(s) to which the event should be emitted. If not
                specified the event is sent to all clients.
        """
        notify: Sequence[str]
        if to is None:
            # Notify all
            notify = tuple(self._sid_to_websocket.keys())

        elif isinstance(to, str):
            # Notify single
            notify = [to]

        else:
            # Notify list of ids.
            pass

        for sid in notify:
            try:
                ws = self._sid_to_websocket.get(sid)
                if ws is not None:
                    dct = {"event": event}
                    if data is not None:
                        dct["data"] = data
                    await ws.send_json(dct)
            except Exception:
                log.exception(f"Error notifying client: {sid}")

    async def manage_websocket(self, websocket: WebSocket):
        """
        Registers a client websocket so that it's possible to talk to
        it from the server.
        """
        sid = self._gen_id()
        self._sid_to_websocket[sid] = websocket
        await self._notify("connect", sid)

        try:
            while True:
                data = await websocket.receive_json()
                if not isinstance(data, dict):
                    log.critical(f"Expected to receive json dict. Found: {data}")
                    continue

                event = data.get("event")
                if not event:
                    log.critical(
                        f"Expected to receive json dict with event. Found: {data}"
                    )
                    continue

                if "data" in data:
                    await self._notify(event, sid, data["data"])
                else:
                    await self._notify(event, sid)

        except WebSocketDisconnect:
            log.debug("Client disconnected from websocket.")
        except Exception:
            log.exception("Unexpected exception from websocket.")
        finally:
            await self._notify("disconnect", sid)
            self._sid_to_websocket.pop(sid, None)

    async def _notify(self, event: str, sid: str, *args):
        handlers = self.event_handlers.get(event)
        if handlers:
            for handler in handlers:
                try:
                    await handler(sid, *args)
                except Exception:
                    log.exception("Unexpected exception in handler.")


_socket_server = SocketServer()


@_socket_server.on("connect")
async def handle_connect(sid: str):
    pass
    # print("Connected", sid)


@_socket_server.on("disconnect")
async def handle_disconnect(sid: str):
    # print("Disconnected", sid)
    from robocorp.action_server._runs_state_cache import get_global_runs_state

    global_runs_state = get_global_runs_state()

    with global_runs_state.semaphore:
        _socket_server.leave_room(sid, "clients_listening_runs")
        if not _socket_server.get_room_sids("clients_listening_runs"):
            # No one listening: no need to listen for run changes
            if _socket_server.on_run_change_callback is not None:
                global_runs_state.unregister(_socket_server.on_run_change_callback)
                _socket_server.on_run_change_callback = None


@_socket_server.on("echo")
async def handle_echo(sid: str, data):
    # Just echo something (testing)
    await _socket_server.emit("echo", data, to=sid)


@_socket_server.on("request")
async def handle_request(sid: str, request_data):
    from starlette.concurrency import run_in_threadpool

    method = request_data.get("method")
    loop = asyncio.get_running_loop()
    if method == "GET":
        message_id = request_data.get("message_id")
        url = request_data.get("url")
        if url == "/api/actionPackages":

            async def _report_listed_actions(message: dict):
                await _socket_server.emit(
                    message["message_type"], message["data"], to=sid
                )

            def on_listed_actions(message: dict):
                asyncio.run_coroutine_threadsafe(_report_listed_actions(message), loop)

            loop.create_task(
                run_in_threadpool(
                    partial(
                        _list_actions_in_threadpool,
                        on_listed_actions,
                        message_id,
                    )
                )
            )


@_socket_server.on("start_listen_run_events")
async def handle_start_listen_run_events(sid: str):
    from robocorp.action_server._runs_state_cache import get_global_runs_state

    global_runs_state = get_global_runs_state()
    loop = asyncio.get_running_loop()

    with global_runs_state.semaphore:
        runs = global_runs_state.get_current_run_state()
        await _report_runs(sid, runs)
        if not _socket_server.get_room_sids("clients_listening_runs"):
            # Start listening if this is the first client added.
            if _socket_server.on_run_change_callback is None:
                _socket_server.on_run_change_callback = partial(
                    _on_run_change_found_in_thread, loop
                )
                global_runs_state.register(_socket_server.on_run_change_callback)

        _socket_server.enter_room(sid, "clients_listening_runs")


async def _report_runs(sid: str, runs: list["Run"]):
    await _socket_server.emit("runs_collected", [asdict(run) for run in runs], to=sid)


def _on_run_change_found_in_thread(loop, run_change_event: "RunChangeEvent"):
    """
    Note that this callback is called from a different thread.
    """
    asyncio.run_coroutine_threadsafe(_report_change_event(run_change_event), loop)


async def _report_change_event(run_change_event: "RunChangeEvent"):
    try:
        # i.e.: send the notification to all connected websockets when found.
        notify_all = None

        if run_change_event.ev == "added":
            await _socket_server.emit(
                "run_added", {"run": asdict(run_change_event.run)}, to=notify_all
            )
        elif run_change_event.ev == "changed":
            await _socket_server.emit(
                "run_changed",
                {
                    "run_id": run_change_event.run.id,
                    "changes": run_change_event.changes,
                },
                to=notify_all,
            )
        else:
            log.critical(f"Unexpected run change event: {run_change_event}.")
    except Exception:
        log.exception("Error reporting change event to json.")


@websocket_api_router.websocket("")
async def websocket_endpoint(websocket: WebSocket):
    await websocket.accept()
    await _socket_server.manage_websocket(websocket)


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
