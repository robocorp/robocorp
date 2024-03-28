import asyncio
import json
import logging
import sys
import threading
from queue import Queue
from typing import Any

import pytest
from action_server_tests.fixtures import ActionServerProcess

log = logging.getLogger(__name__)


class AsyncIOThread(threading.Thread):
    """
    Note: we could use something as:

    @pytest.fixture
    def anyio_backend():
        return 'asyncio'

    pytestmark = pytest.mark.anyio

    And then create "async def test"

    But this messes up robocorp-log-pytest (which doesn't handle async).

    So, we create a thread to deal with the async part.
    """

    def __init__(self):
        threading.Thread.__init__(self)
        self.loop = asyncio.new_event_loop()

    def run(self):
        self.loop.run_forever()

    def submit_async(self, awaitable):
        return asyncio.run_coroutine_threadsafe(awaitable, self.loop)

    def stop_async(self):
        self.loop.call_soon_threadsafe(self.loop.stop)

    def websocket_connect(self, url):
        self.submit_async(self._connect(url))


@pytest.fixture
def asyncio_thread():
    asyncio_thread = AsyncIOThread()
    asyncio_thread.start()
    yield asyncio_thread
    asyncio_thread.stop_async()
    asyncio_thread.join()


def build_ws_url(action_server_process, url="api/ws"):
    host = action_server_process.host
    port = action_server_process.port
    if url.startswith("/"):
        url = url[1:]
    return f"ws://{host}:{port}/{url}"


class SocketClient:
    def __init__(self, ws):
        self.ws = ws

    async def emit(self, event, data=None):
        msg = {"event": event}
        if data is not None:
            msg["data"] = data
        await self.ws.send(json.dumps(msg))

    async def receive(self):
        received = json.loads(await self.ws.recv())
        return received["event"], received.get("data")


async def check_websocket_runs(
    action_server_process: ActionServerProcess, queue: Queue[Any]
):
    try:
        url = build_ws_url(action_server_process)

        import websockets

        async with websockets.connect(
            url, logger=log, open_timeout=_get_timeout()
        ) as ws:
            sio = SocketClient(ws)
            await sio.emit("echo", "echo-val")

            event, val = await sio.receive()
            assert event == "echo"
            assert val == "echo-val"

            # Ok, echo is there, let's start to listen run events
            await sio.emit("start_listen_run_events")

            # First message has the runs currently available
            event, runs = await sio.receive()
            assert event == "runs_collected"
            assert runs == []

            # Request for a run to be created
            queue.put("create_run")

            # Run was created
            event, added = await sio.receive()
            assert tuple(added.keys()) == ("run",)
            assert added["run"]["numbered_id"] == 1
            assert event == "run_added"

            # Run was changed (running -> complete)
            event, changed = await sio.receive()
            assert tuple(changed.keys()) == ("run_id", "changes")
            assert event == "run_changed"

    except Exception as e:
        import traceback

        traceback.print_exc()
        queue.put(e)
    else:
        queue.put("worked")


async def check_websocket_action_package(
    action_server_process: ActionServerProcess, queue: Queue[Any]
):
    try:
        url = build_ws_url(action_server_process)

        import websockets

        async with websockets.connect(
            url, logger=log, open_timeout=_get_timeout()
        ) as ws:
            sio = SocketClient(ws)

            await sio.emit(
                "request",
                {
                    "method": "GET",
                    "url": "/api/actionPackages",
                    "message_id": 22,
                },
            )

            event, data = await sio.receive()
            assert event == "response", f"Received unexpected: {event!r}"
            assert data["message_id"] == 22, f"Received unexpected: {data!r}"
            assert len(data["result"]) == 2, f"Received unexpected: {data!r}"
    except Exception as e:
        queue.put(e)
    else:
        queue.put("worked")


def _get_timeout():
    if "pydevd" in sys.modules:
        return None
    return 20


def test_server_websockets(
    action_server_process: ActionServerProcess,
    asyncio_thread: AsyncIOThread,
    base_case,
    client,
) -> None:
    queue: Queue[Any] = Queue()
    asyncio_thread.submit_async(check_websocket_runs(action_server_process, queue))
    while True:
        curr = queue.get(timeout=_get_timeout())
        if curr == "worked":
            break

        if curr == "create_run":
            client.post_get_str(
                "api/actions/greeter/greet/run", {"name": "Foo", "title": "Mr."}
            )
        else:
            raise AssertionError(curr)

    asyncio_thread.submit_async(
        check_websocket_action_package(action_server_process, queue)
    )
    while True:
        curr = queue.get(timeout=_get_timeout())
        if curr == "worked":
            break

        else:
            raise AssertionError(curr)
