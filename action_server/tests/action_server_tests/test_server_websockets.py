import asyncio
import json
import logging
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


def build_ws_url(action_server_process, url):
    host = action_server_process.host
    port = action_server_process.port
    if url.startswith("/"):
        url = url[1:]
    return f"ws://{host}:{port}/{url}"


async def check_websocket_runs(
    action_server_process: ActionServerProcess, queue: Queue[Any]
):
    try:
        url = build_ws_url(action_server_process, "api/ws")

        import websockets

        async with websockets.connect(
            url,
            logger=log,
        ) as ws:
            await ws.send(json.dumps({"message_type": "ping"}))

            received = json.loads(await ws.recv())
            assert received == {
                "message_type": "pong"
            }, f"Received unexpected: {received!r}"

            # Ok, echo is there, let's start to listen run events
            await ws.send(json.dumps({"message_type": "start_listen_run_events"}))

            # First message has the runs currently available
            current_run_events = json.loads(await ws.recv())
            assert current_run_events["message_type"] == "runs_collected"

            # Request for a run to be created
            queue.put("create_run")

            # Run was created
            current_run_events = json.loads(await ws.recv())
            assert current_run_events["message_type"] == "run_added"

            # Run was changed (running -> complete)
            current_run_events = json.loads(await ws.recv())
            assert current_run_events["message_type"] == "run_changed"

    except Exception as e:
        queue.put(e)
    else:
        queue.put("worked")


async def check_websocket_action_package(
    action_server_process: ActionServerProcess, queue: Queue[Any]
):
    try:
        url = build_ws_url(action_server_process, "api/ws")

        import websockets

        async with websockets.connect(
            url,
            logger=log,
        ) as ws:
            await ws.send(
                json.dumps(
                    {
                        "message_type": "request",
                        "data": {
                            "method": "GET",
                            "url": "/api/actionPackages",
                            "message_id": 22,
                        },
                    }
                )
            )

            received = json.loads(await ws.recv())
            {
                "message_type": "response",
                "data": {
                    "message_id": 22,
                    "result": [],
                },
            }
            assert (
                received["message_type"] == "response"
            ), f"Received unexpected: {received!r}"
            assert (
                received["data"]["message_id"] == 22
            ), f"Received unexpected: {received!r}"
            assert (
                len(received["data"]["result"]) == 2
            ), f"Received unexpected: {received!r}"
    except Exception as e:
        queue.put(e)
    else:
        queue.put("worked")


def test_server_websockets(
    action_server_process: ActionServerProcess,
    asyncio_thread: AsyncIOThread,
    base_case,
    client,
) -> None:
    queue: Queue[Any] = Queue()
    asyncio_thread.submit_async(check_websocket_runs(action_server_process, queue))
    while True:
        curr = queue.get(timeout=20)
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
        curr = queue.get(timeout=20)
        if curr == "worked":
            break

        else:
            raise AssertionError(curr)
