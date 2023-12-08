import asyncio
import logging
import threading
import typing
from dataclasses import asdict

from fastapi.routing import APIRouter
from starlette.websockets import WebSocket, WebSocketDisconnect

if typing.TYPE_CHECKING:
    from ._models import Run
    from ._runs_state_cache import RunChangeEvent

log = logging.getLogger(__name__)


websocket_api_router = APIRouter(prefix="/api/ws")


class RunNotificationsThread(threading.Thread):
    def __init__(self, loop, websocket):
        super().__init__()

        self.loop = loop
        self.websocket = websocket
        self._disposed = threading.Event()
        self.daemon = True

    def __call__(self, run_change_event: "RunChangeEvent"):
        asyncio.run_coroutine_threadsafe(
            self._report_change_event(run_change_event), self.loop
        )

    def run(self):
        # Collect the runs, send them and register for additional changes until
        # `dispose` is called.
        from robocorp.action_server._runs_state_cache import get_global_runs_state

        global_runs_state = get_global_runs_state()

        with global_runs_state.semaphore:
            runs = global_runs_state.get_current_run_state()
            asyncio.run_coroutine_threadsafe(self._report_runs(runs), self.loop)
            global_runs_state.register(self)

        try:
            self._disposed.wait()
        finally:
            with global_runs_state.semaphore:
                global_runs_state.unregister(self)

    async def _report_change_event(self, run_change_event: "RunChangeEvent"):
        """
        This is run in asyncio, not in this thread.
        """
        if self._disposed.is_set():
            return

        try:
            if run_change_event.ev == "added":
                await self.websocket.send_json(
                    {
                        "message_type": "run_added",
                        "run": asdict(run_change_event.run),
                    }
                )
            elif run_change_event.ev == "changed":
                await self.websocket.send_json(
                    {
                        "message_type": "run_changed",
                        "run_id": run_change_event.run.id,
                        "changes": run_change_event.changes,
                    }
                )
            else:
                log.critical(f"Unexpected run change event: {run_change_event}.")
        except Exception:
            log.exception("Error reporting change event to json.")
            raise

    async def _report_runs(self, runs: list["Run"]):
        """
        This is run in asyncio, not in this thread.
        """
        if self._disposed.is_set():
            return

        await self.websocket.send_json(
            {
                "message_type": "runs_collected",
                "runs": [asdict(run) for run in runs],
            }
        )

    def dispose(self):
        """
        Disposes of this thread.
        """
        self._disposed.set()


@websocket_api_router.websocket("")
async def websocket_endpoint(websocket: WebSocket):
    loop = asyncio.get_running_loop()

    await websocket.accept()
    run_notifications = RunNotificationsThread(loop, websocket)
    try:
        while True:
            data = await websocket.receive_json()
            message_type = data.get("message_type")
            if message_type == "ping":
                await websocket.send_json({"message_type": "pong"})

            elif message_type == "start_listen_run_events":
                # In this case we have to:
                # 1. Send the current runs to the client.
                # 2. When run changes are done, notify the client.
                # The thread should take care of this after it's started.
                if not run_notifications.is_alive():
                    run_notifications.start()
                else:
                    # If the client calls start_listen_run_events, should we send
                    # it again? Right now clients are not expected to do that, so
                    # just log it and ignore.
                    log.info('Ignoring additional call to "start_listen_run_events"')
    except WebSocketDisconnect:
        log.info("Client disconnected from websocket.")
    except Exception:
        log.exception("Unexpected exception from websocket.")
    finally:
        run_notifications.dispose()
