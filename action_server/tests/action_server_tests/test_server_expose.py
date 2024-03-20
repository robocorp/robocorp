import asyncio
import concurrent.futures
import json
import socket
import threading
import uuid
from queue import Queue

import pytest

from robocorp.action_server._selftest import ActionServerProcess


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
        dummy_robocorp_link_server.websocket_url = f"wss://{dummy_host}:{dummy_port}"
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
