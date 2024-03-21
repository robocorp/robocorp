import asyncio
import json
import threading
import typing
from concurrent import futures
from queue import Queue
from typing import TypeVar

from robocorp.action_server._selftest import ActionServerProcess

T = TypeVar("T")


def wait_for_expose_session_info(action_server_process):
    import time
    from json import JSONDecodeError

    timeout_at = time.time() + 15
    target = action_server_process.datadir / "expose_session.json"
    while time.time() < timeout_at:
        try:
            expose_session_info = json.loads(target.read_text())
            return expose_session_info
        except (FileNotFoundError, JSONDecodeError):
            continue

    raise AssertionError(f"The file: {target} was not generated in the given timeout.")


def manual_test_server_expose(
    datadir,
    action_server_process: ActionServerProcess,
    data_regression,
):
    """
    Tests the action server --expose against the real server.
    """
    from robocorp.action_server._selftest import ActionServerClient

    action_server_process.start(
        db_file="server.db",
        cwd=datadir,
        actions_sync=True,
        timeout=300,
        lint=True,
        min_processes=2,
        max_processes=2,
        reuse_processes=True,
        additional_args=["--expose"],
    )

    expose_session_info = wait_for_expose_session_info(action_server_process)
    api_key = (action_server_process.datadir / ".api_key").read_text()

    target_url = expose_session_info["url"]
    headers = {"Authorization": f"Bearer {api_key}"}

    client = ActionServerClient(target_url)
    openapi = json.loads(client.get_openapi_json())
    assert openapi.pop("servers") == [{"url": target_url}]

    data_regression.check(openapi)

    from robocorp.action_server._robo_utils.run_in_thread import run_in_thread

    def call_sleep(time_to_sleep: float):
        def func():
            ret = client.post_get_str(
                "/api/actions/test-server-expose/sleep-a-while/run",
                {"time_to_sleep": time_to_sleep},
                headers=headers,
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


def run_in_loop(loop: asyncio.AbstractEventLoop, func, timeout=10):
    fut: futures.Future = futures.Future()

    def callback():
        try:
            result = func()
        except BaseException as e:
            fut.set_exception(e)
        else:
            fut.set_result(result)

    loop.call_soon_threadsafe(callback)
    return fut.result(timeout)


def run_coro_in_loop(loop: asyncio.AbstractEventLoop, coro, timeout=10):
    fut: futures.Future = futures.Future()

    async def callback():
        try:
            result = await coro
        except BaseException as e:
            fut.set_exception(e)
        else:
            fut.set_result(result)

    asyncio.run_coroutine_threadsafe(callback(), loop)
    return fut.result(timeout)


def manual_test_server_expose_local(
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

    websocket_expose_url = "ws://127.0.0.1:8787"

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
                expose_url=websocket_expose_url,  # localhost
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

    connected_ev = wait_for_ev(EventConnected)
    session_payload_ev = wait_for_ev(EventSessionPayload)

    target_url = "http://127.0.0.1:8787"
    params = {"sessionId": session_payload_ev.session_payload.sessionId}

    client = ActionServerClient(target_url)
    data_regression.check(json.loads(client.get_openapi_json(params=params)))

    # Close the connection: a new one must be done.
    run_coro_in_loop(loop, connected_ev.ws.close())
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
    run_in_loop(loop, listen_task.cancel)
    wait_for_ev(EventTaskListenForRequestsFinished)
    server_expose_thread.join(timeout=2)
    assert not server_expose_thread.is_alive()


# def manual_tests_on_url():
#     from robocorp.action_server._selftest import ActionServerClient
#
#     url = "https://twenty-four-tame-rabbits.robocorp.link"
#     client = ActionServerClient(url)
#     print(client.get_openapi_json())
#     print(
#         client.post_get_str(
#             "/api/actions/action-package/tell-me-some-joke/run",
#             {"joke_theme": "Some theme"},
#             {"Authorization": "Bearer <token>"},
#         )
#     )
