import asyncio
import concurrent.futures
import json
import socket
import threading
import typing
import uuid
from concurrent import futures
from queue import Queue
from typing import TypeVar

import pytest

from robocorp.action_server._selftest import ActionServerProcess

T = TypeVar("T")


class DummyRobocorpLinkWebsocketServer:
    """
    This class is a dummy class to test websocket connections.

    When a connection is received, the first message it sends is a message
    with the session id and the related secret (so that the session can be
    reconnected again later on).

    Example:

        {"sessionId":"my-custom-session-id","sessionSecret":"secret-string"}

    Internally it has 2 queues, a write queue, where information may be written
    to which should be written to the websocket and a read queue, where information
    can be read from.

    Also, it should continually send a message with a "pong" string and then
    check if a "ping" is received after some timeout (if it's not received
    the connection can be considered closed).
    """

    def __init__(self):
        self.write_queue = Queue()
        self.read_queue = Queue()
        self.session_id = str(uuid.uuid4())
        self.session_secret = str(uuid.uuid4())
        self.websocket = None
        self.pong_task = None
        self.websocket_url = ""
        self.log_info = ["initial"]

    async def handle_connection(self, websocket):
        self.log_info.append("connected")
        self.websocket = websocket
        await self.send_session_info()
        self.log_info.append("sent session info")
        await self.start_ping_pong_loop()
        self.log_info.append("started ping-pong")

        try:
            while True:
                message = await self.read_message()
                await self.handle_message(message)
        except asyncio.CancelledError:
            pass
        finally:
            await self.cleanup_connection()

    async def send_session_info(self):
        session_info = {
            "sessionId": self.session_id,
            "sessionSecret": self.session_secret,
        }
        await self.websocket.send(json.dumps(session_info))

    async def start_ping_pong_loop(self):
        self.pong_task = asyncio.create_task(self.pong_loop())

    async def pong_loop(self):
        while True:
            await self.websocket.send("pong")
            try:
                await asyncio.wait_for(self.websocket.recv(), timeout=5)
            except asyncio.TimeoutError:
                await self.close_connection()
                return

    async def handle_message(self, message):
        self.read_queue.put(message)

    async def write_message(self, message):
        await self.websocket.send(message)

    async def read_message(self):
        message = await self.websocket.recv()
        self.write_queue.put(message)  # For testing purposes
        return message

    async def close_connection(self):
        if self.pong_task:
            self.pong_task.cancel()
        await self.websocket.close()

    async def cleanup_connection(self):
        await self.close_connection()
        self.websocket = None
        self.pong_task = None


def _start_dummy_server(
    dummy_server: DummyRobocorpLinkWebsocketServer,
    stop: asyncio.Future,
    host_port_future: concurrent.futures.Future,
):
    async def start() -> None:  # Add a start method to create the server
        import websockets

        async with websockets.serve(
            dummy_server.handle_connection, "localhost", 0
        ) as server:
            for s in server.server.sockets:
                if s.family == socket.AF_INET:
                    host, port = s.getsockname()
                    host_port_future.set_result((host, port))
                    break
            else:
                raise RuntimeError("Unable to find ipv4 socket")

            await stop
            server.close()

    asyncio.run(start())


@pytest.fixture
def dummy_robocorp_link_server():
    dummy_robocorp_link_server = DummyRobocorpLinkWebsocketServer()
    stop = asyncio.Future()

    try:
        # Start the dummy server.
        host_port_future = concurrent.futures.Future()

        t_dummy = threading.Thread(
            target=_start_dummy_server,
            args=(dummy_robocorp_link_server, stop, host_port_future),
            name="_Dummy Server (robocorp.link)",
        )
        t_dummy.start()
        dummy_host, dummy_port = host_port_future.result(5)
        dummy_robocorp_link_server.websocket_url = f"ws://{dummy_host}:{dummy_port}"
        print(f"Dummy server started at: {dummy_robocorp_link_server.websocket_url}")

        yield dummy_robocorp_link_server

    finally:
        stop.set_result("done")


def todo_test_server_expose(
    datadir,
    dummy_robocorp_link_server: DummyRobocorpLinkWebsocketServer,
    action_server_process: ActionServerProcess,
):
    """
    Note: this test is unfinished and is marked as todo...
    Hopefully this is tackled when we touch the server expose code again!
    """
    # Start the action server.

    # Start the server expose (in this case, requests will be
    # sent to the dummy server and then should be forwarded to
    # the action server -- and its result should be sent back
    # afterwards).
    from action_server_tests.fixtures import get_in_resources

    calculator = get_in_resources("no_conda", "calculator")
    action_server_process.start(
        db_file="server.db",
        cwd=calculator,
        actions_sync=True,
        timeout=300,
        lint=False,
    )

    host = action_server_process.host
    port = action_server_process.port

    assert dummy_robocorp_link_server.websocket_url

    parent_pid = ""
    config_logging = True
    api_key = "this-is-the-api-key"

    args = [
        parent_pid,
        str(port),
        "v",  # verbose
        host,
        dummy_robocorp_link_server.websocket_url,
        str(datadir),
        "None",
        api_key,
        config_logging,
    ]

    from robocorp.action_server import _server_expose

    t1 = threading.Thread(
        target=_server_expose.main, args=args, name="Server Expose Thread"
    )
    t1.start()

    # Ok, the full setup should be done at this point. Let's start
    # the actual testing.

    print("started")
    print("test...")


def todo_test_server_expose_local(
    datadir,
    action_server_process: ActionServerProcess,
    data_regression,
) -> None:
    """
    This tests the "real" exposed server but in a local version.

    To work it requires `action-server-tunnel` (private repo).

    -- After cloning it must be bootstrapped with:

    npm i
    npm dev

    Then this test can be run.
    """
    from robocorp.action_server import _server_expose
    from robocorp.action_server._robo_utils.run_in_thread import run_in_thread
    from robocorp.action_server._selftest import ActionServerClient
    from robocorp.action_server._server_expose import (
        EventAsyncIOLoop,
        EventConnected,
        EventSessionPayload,
        EventTaskListenForRequests,
        EventTaskListenForRequestsFinished,
        ServerEvent,
    )

    action_server_process.start(
        db_file="server.db",
        cwd=datadir,
        actions_sync=True,
        timeout=300,
        lint=True,
        min_processes=2,
        max_processes=2,
        reuse_processes=True,
    )

    host = action_server_process.host
    port = action_server_process.port

    events_queue: Queue[ServerEvent] = Queue()

    def wait_for_ev(cls: typing.Type[T]) -> T:
        while True:
            try:
                ev = events_queue.get(timeout=3)
            except Exception:
                raise AssertionError(f"Timed out waiting for event of type: {cls}")
            if isinstance(ev, cls):
                return ev
            # If it wasn't, wait for the next event.

    def expose():
        _server_expose._setup_logging(force=True)
        asyncio.run(
            _server_expose.expose_server(
                port=int(port),
                host=host,
                expose_url="ws://127.0.0.1:8787",  # localhost
                datadir=datadir,
                expose_session=None,
                api_key=None,
                on_event=events_queue.put,
            )
        )

    server_expose_thread = threading.Thread(
        target=expose, name="Server Expose Thread", daemon=True
    )
    server_expose_thread.start()

    loop_ev = wait_for_ev(EventAsyncIOLoop)
    listen_task: asyncio.Task = wait_for_ev(EventTaskListenForRequests).task
    loop: asyncio.AbstractEventLoop = loop_ev.loop

    def run_in_loop(func, timeout=10):
        fut = futures.Future()

        def callback():
            try:
                result = func()
            except BaseException as e:
                fut.set_exception(e)
            else:
                fut.set_result(result)

        loop.call_soon_threadsafe(callback)
        return fut.result(timeout)

    def run_coro_in_loop(coro, timeout=10):
        fut = futures.Future()

        async def callback():
            try:
                result = await coro
            except BaseException as e:
                fut.set_exception(e)
            else:
                fut.set_result(result)

        asyncio.run_coroutine_threadsafe(callback(), loop)
        return fut.result(timeout)

    connected_ev = wait_for_ev(EventConnected)
    session_payload_ev = wait_for_ev(EventSessionPayload)

    client = ActionServerClient("http://127.0.0.1:8787")
    data_regression.check(
        json.loads(
            client.get_openapi_json(
                params={"sessionId": session_payload_ev.session_payload.sessionId}
            )
        )
    )

    # Close the connection: a new one must be done.
    run_coro_in_loop(connected_ev.ws.close())
    _connected_ev2 = wait_for_ev(EventConnected)
    session_payload_ev2 = wait_for_ev(EventSessionPayload)
    # The session id cannot have changed in the meanwhile.
    assert (
        session_payload_ev2.session_payload.sessionId
        == session_payload_ev.session_payload.sessionId
    )

    def call_sleep(time_to_sleep: float):
        def func():
            ret = client.post_get_str(
                "/api/actions/test-server-expose/sleep-a-while/run",
                {"time_to_sleep": time_to_sleep},
                params={"sessionId": session_payload_ev.session_payload.sessionId},
            )
            return float(ret)

        fut = run_in_thread(func)
        return fut

    first = call_sleep(3)
    second = call_sleep(0.1)

    first_finished_at = first.result(timeout=10)
    second_finished_at = second.result(timeout=10)
    # The second must've finished before the first!
    assert second_finished_at < first_finished_at

    # Teardown
    run_in_loop(listen_task.cancel)
    wait_for_ev(EventTaskListenForRequestsFinished)
    server_expose_thread.join(timeout=2)
    assert not server_expose_thread.is_alive()
