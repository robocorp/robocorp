import asyncio
import codecs
import json
import logging
import os
import socket
import sys
import typing
from dataclasses import dataclass
from typing import Callable, Optional, Tuple

from pydantic import BaseModel, ValidationError
from termcolor import colored

if typing.TYPE_CHECKING:
    import websockets
    from aiohttp import ClientSession

log = logging.getLogger(__name__)


class SessionPayload(BaseModel):
    sessionId: str
    sessionSecret: str


class BodyPayload(BaseModel):
    requestId: str
    path: str
    method: str = "GET"
    body: dict | None = None
    headers: dict


class ExposeSessionJson(BaseModel):
    expose_session: str
    url: str


def get_expose_session_path(datadir: str) -> str:
    return os.path.join(datadir, "expose_session.json")


def read_expose_session_json(datadir: str) -> None | ExposeSessionJson:
    session_json = None
    try:
        expose_session_path = get_expose_session_path(datadir)
        log.debug(f"🗂️ Reading expose_session.json path={expose_session_path}")
        with open(expose_session_path, "r") as f:
            session_json = ExposeSessionJson(**json.load(f))
    except FileNotFoundError:
        pass
    except ValidationError as e:
        log.error("Failed to load previous expose session", e)
    except json.JSONDecodeError as e:
        log.error("Failed to decode exopse session json", e)
    return session_json


def write_expose_session_json(
    datadir: str, expose_session_json: ExposeSessionJson
) -> None:
    expose_session_path = get_expose_session_path(datadir)
    log.debug(f"🗂️ Writing expose_session.json path={expose_session_path}")
    with open(expose_session_path, "w") as f:
        json.dump(
            expose_session_json.model_dump(),
            f,
            indent=2,
        )


def get_expose_session(payload: SessionPayload) -> str:
    return f"{payload.sessionId}:{payload.sessionSecret}".encode("ascii").hex()


def get_expose_session_payload(expose_session: str) -> SessionPayload:
    session_id, session_secret = codecs.decode(
        expose_session.encode("ascii"), "hex"
    ).split(b":")
    return SessionPayload(
        sessionId=session_id.decode(), sessionSecret=session_secret.decode()
    )


async def forward_request_async(
    session: "ClientSession", base_url: str, payload: BodyPayload
) -> Tuple[int, dict]:
    url = base_url.rstrip("/") + "/" + payload.path.lstrip("/")

    async with session.request(
        payload.method, url, json=payload.body, headers=payload.headers
    ) as response:
        return response.status, await response.json()


async def handle_ping_pong(
    ws: "websockets.WebSocketClientProtocol",
    pong_queue: asyncio.Queue,
    ping_interval: int,
):
    while True:
        await asyncio.sleep(ping_interval)
        await ws.send("ping")

        try:
            await asyncio.wait_for(pong_queue.get(), timeout=ping_interval)
        except (asyncio.TimeoutError, TimeoutError):
            log.debug("Lost connection to expose server")
            await ws.close()
            break


def handle_session_payload(
    session_payload: SessionPayload, expose_url: str, datadir: str, api_key: str | None
):
    url = f"https://{session_payload.sessionId}.{expose_url}"
    log.info(
        colored("  🌍 Public URL: ", "green", attrs=["bold"])
        + colored(f"{url}", "light_blue")
    )
    if api_key:
        log.info(
            colored("  🔑 API Authorization Bearer key: ", attrs=["bold"])
            + f"{api_key}\n"
        )
    new_expose_session = get_expose_session(session_payload)
    write_expose_session_json(
        datadir=datadir,
        expose_session_json=ExposeSessionJson(
            expose_session=new_expose_session,
            url=url,
        ),
    )


async def handle_body_payload(
    session: "ClientSession",
    ws: "websockets.WebSocketClientProtocol",
    payload: BodyPayload,
    base_url: str,
):
    try:
        status, json_dict = await forward_request_async(
            session=session, base_url=base_url, payload=payload
        )
        response_converted = json.dumps(
            {
                "requestId": payload.requestId,
                "response": json.dumps(
                    json_dict,
                    indent=2,
                ),
                "status": status,
            }
        )

        await ws.send(response_converted)
    except Exception:
        log.exception("Error handling body payload")


def _headers_from_session_payload(session_payload: SessionPayload):
    headers = {
        "x-session-id": session_payload.sessionId,
        "x-session-secret": session_payload.sessionSecret,
    }
    return headers


class ServerEvent:
    pass


@dataclass
class EventConnected(ServerEvent):
    ws: "websockets.WebSocketClientProtocol"


@dataclass
class EventMessage(ServerEvent):
    message: str | bytes


@dataclass
class EventSessionPayload(ServerEvent):
    session_payload: SessionPayload


@dataclass
class EventAsyncIOLoop(ServerEvent):
    loop: asyncio.AbstractEventLoop


@dataclass
class EventTaskListenForRequests(ServerEvent):
    task: asyncio.Task


class EventTaskListenForRequestsFinished(ServerEvent):
    pass


async def expose_server(
    port: int,
    host: str,
    expose_url: str,
    datadir: str,
    expose_session: str | None = None,
    ping_interval: int = 4,
    api_key: str | None = None,
    on_event: Callable[[ServerEvent], None] | None = None,
):
    """
    Exposes the server to the world.
    """
    import websockets

    pong_queue: asyncio.Queue = asyncio.Queue(maxsize=1)
    if on_event is not None:
        loop = asyncio.get_running_loop()
        on_event(EventAsyncIOLoop(loop))

    async def listen_for_requests() -> None:
        from aiohttp import ClientSession

        session_payload: Optional[SessionPayload] = (
            get_expose_session_payload(expose_session) if expose_session else None
        )

        headers = (
            _headers_from_session_payload(session_payload) if session_payload else {}
        )

        # In testing wss:// is added (in production it's just robocorp.link and
        # we connect to wss://client.robocorp.link and when we receive the session
        # id/secret we print it as: https://{session_payload.sessionId}.{expose_url}).
        if not expose_url.startswith("wss://") and not expose_url.startswith("ws://"):
            use_url = f"wss://client.{expose_url}"
        else:
            use_url = expose_url

        ws: websockets.WebSocketClientProtocol
        async with ClientSession() as session:
            async for ws in websockets.connect(
                use_url,
                extra_headers=headers,
                logger=log,
                open_timeout=2,
                close_timeout=0,
            ):
                if on_event is not None:
                    on_event(EventConnected(ws))
                ping_task = asyncio.create_task(
                    handle_ping_pong(ws, pong_queue, ping_interval)
                )

                try:
                    while True:
                        message = await ws.recv()
                        if on_event is not None:
                            on_event(EventMessage(message))

                        if message == "pong":
                            await pong_queue.put("pong")
                            continue

                        data = json.loads(message)

                        match data:
                            case {"sessionId": _, "sessionSecret": _}:
                                try:
                                    session_payload = SessionPayload(**data)
                                    if on_event is not None:
                                        on_event(EventSessionPayload(session_payload))
                                    # Make sure that after we connect the session is
                                    # always the same for reconnects.
                                    # Note: tricky detail: because we're reconnecting
                                    # in the above `for` which already has the `extra_headers`
                                    # bound, we just update the headers in-place...
                                    # this could fail in the future is websockets.connect
                                    # for some reason does a copy of the extra headers,
                                    # so, we have to be careful (probably not the best
                                    # approach, but working for a fast fix).
                                    headers.update(
                                        _headers_from_session_payload(session_payload)
                                    )
                                    handle_session_payload(
                                        session_payload, expose_url, datadir, api_key
                                    )
                                except ValidationError as e:
                                    if not session_payload:
                                        log.error(
                                            "Expose session initialization failed", e
                                        )
                                        continue
                            case _:
                                try:
                                    body_payload = BodyPayload(**data)
                                    asyncio.create_task(
                                        handle_body_payload(
                                            session,
                                            ws,
                                            body_payload,
                                            f"http://{host}:{port}",
                                        )
                                    )
                                except ValidationError as e:
                                    log.error("Expose request validation failed", e)
                                    continue
                except websockets.exceptions.ConnectionClosedError:
                    log.info("Lost connection. Reconnecting to expose server...")
                except socket.gaierror as e:
                    log.info(f"Socket error: {e}")
                except Exception as e:
                    log.error(f"Unexpected exception: {e}")
                finally:
                    ping_task.cancel()
                    try:
                        await ping_task
                    except asyncio.CancelledError:
                        pass
            else:
                log.info("Expose server connection closed")

    task = asyncio.create_task(listen_for_requests())
    if on_event is not None:
        on_event(EventTaskListenForRequests(task))
    try:
        await task  # Wait for listen_for_requests to complete
    except asyncio.CancelledError:
        log.info("Expose server listen requests cancelled.")
    finally:
        if on_event is not None:
            on_event(EventTaskListenForRequestsFinished())


def _setup_logging(verbose="v", force=False):
    logging.basicConfig(
        level=logging.DEBUG if verbose.count("v") > 0 else logging.INFO,
        format="%(message)s",
        datefmt="[%X]",
        force=force,
    )

    def remove_traceback(record):
        if record.levelname == "INFO":
            if record.exc_info:
                record.exc_info = None
        return True

    # Don't bee too verbose when attempting to reconnect.
    log.addFilter(remove_traceback)


def main(
    parent_pid: str,
    port: str,
    verbose: str,
    host: str,
    expose_url: str,
    datadir: str,
    expose_session: str,
    api_key: str | None,
    config_logging: bool = True,
) -> None:
    """
    Args:
        parent_pid:
            The pid of the parent (when the given pid exists, this process must
            also exit itself). If it's an empty string, it's ignored.

        verbose:
            A string with `v` chars (currently a single `v` means debug, otherwise
            info).

        host:
            The host to where the data should be forwarded.

        port:
            The port to where the data should be forwarded.

        expose_url:
            The url for the expose (usually "robocorp.link").

            Note that the protocol here is that it'll connect to something as:

            wss://client.{expose_url}

            Which will then provide a message with a payload such as:

                {"sessionId": _, "sessionSecret": _}

            and then the server will start accepting connections at:

            https://{session_payload.sessionId}.{expose_url}

            and then messages can be sent to that address to be received
            by the action server.

        datadir:
            The directory where the expose session information should
            be stored.

        expose_session:
            A string with the information of a previous session which
            should be restored (or 'None' if there's no previous session
            information to be restored).

        api_key:
            The api key that should be passed to the action server along with
            the forwarded messages so that the action server accepts it.
    """
    from robocorp.action_server._robo_utils.process import exit_when_pid_exists

    if config_logging:
        _setup_logging(verbose)

    if parent_pid:
        exit_when_pid_exists(int(parent_pid))

    try:
        asyncio.run(
            expose_server(
                port=int(port),
                host=host,
                expose_url=expose_url,
                datadir=datadir,
                expose_session=expose_session if expose_session != "None" else None,
                api_key=api_key,
            )
        )
    except KeyboardInterrupt:
        pass


if __name__ == "__main__":
    try:
        (
            parent_pid,
            port,
            verbose,
            host,
            expose_url,
            datadir,
            expose_session,
            api_key,
        ) = sys.argv[1:]
    except Exception:
        raise RuntimeError(f"Unable to initialize with sys.argv: {sys.argv}")

    main(
        parent_pid,
        port,
        verbose,
        host,
        expose_url,
        datadir,
        expose_session,
        api_key,
    )
