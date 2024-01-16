import asyncio
import codecs
import json
import logging
import os
import socket
import sys
from typing import Optional

import requests
import websockets
from pydantic import BaseModel, ValidationError

from robocorp.action_server._robo_utils.process import exit_when_pid_exists

log = logging.getLogger(__name__)

# disable websockets logger. It's too verbose
websockets_logger = logging.getLogger("websockets")
websockets_logger.setLevel(logging.ERROR)


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
    api_key: str | None = None


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


def forward_request(base_url: str, payload: BodyPayload) -> requests.Response:
    url = base_url.rstrip("/") + "/" + payload.path.lstrip("/")

    if payload.method == "GET":
        return requests.get(url, headers=payload.headers)
    elif payload.method == "POST":
        return requests.post(url, json=payload.body, headers=payload.headers)
    elif payload.method == "PUT":
        return requests.put(url, json=payload.body, headers=payload.headers)
    elif payload.method == "DELETE":
        return requests.delete(url, headers=payload.headers)
    else:
        raise NotImplementedError(f"Method {payload.method} not implemented")


async def handle_ping_pong(
    ws: websockets.WebSocketClientProtocol,
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
    session_payload: SessionPayload, api_key: str, expose_url: str, datadir: str
) -> None:
    url = f"https://{session_payload.sessionId}.{expose_url}"
    log.info(f"🌍 URL: {url}")
    if api_key is not None:
        log.info(
            f'🔑 Add following header api authorization header to run actions: {{ "Authorization": "Bearer {api_key}" }}'  # noqa
        )
    new_expose_session = get_expose_session(session_payload)
    write_expose_session_json(
        datadir=datadir,
        expose_session_json=ExposeSessionJson(
            expose_session=new_expose_session,
            api_key=api_key,
            url=url,
        ),
    )


def handle_body_payload(
    payload: BodyPayload,
    api_key: str,
    base_url: str,
) -> str:
    if payload.path != "/openapi.json" and api_key is not None:
        if payload.headers.get("authorization") != f"Bearer {api_key}":
            log.error("Request failed because the API key is invalid.")
            return json.dumps(
                {
                    "requestId": payload.requestId,
                    "response": json.dumps(
                        {
                            "error": {
                                "code": "INVALID_API_KEY",
                                "message": "The API key is invalid.",
                            },
                        }
                    ),
                    "status": 403,
                }
            )

    response: requests.Response = forward_request(base_url=base_url, payload=payload)
    return json.dumps(
        {
            "requestId": payload.requestId,
            "response": json.dumps(
                response.json(),
                indent=2,
            ),
            "status": response.status_code,
        }
    )


async def expose_server(
    port: int,
    host: str,
    expose_url: str,
    datadir: str,
    api_key: str | None = None,
    expose_session: str | None = None,
    ping_interval: int = 4,
):
    """
    Exposes the server to the world.
    """

    pong_queue: asyncio.Queue = asyncio.Queue(maxsize=1)

    async def listen_for_requests() -> None:
        max_retries = 3
        retry_delay = 3
        retries = 0

        session_payload: Optional[SessionPayload] = (
            get_expose_session_payload(expose_session) if expose_session else None
        )

        headers = (
            {
                "x-session-id": session_payload.sessionId,
                "x-session-secret": session_payload.sessionSecret,
            }
            if session_payload
            else {}
        )

        async for ws in websockets.connect(
            f"wss://client.{expose_url}",
            extra_headers=headers,
            logger=websockets_logger,
        ):
            if retries > 0:
                retries = 0

            ping_task = asyncio.create_task(
                handle_ping_pong(ws, pong_queue, ping_interval)
            )

            try:
                while True:
                    message = await ws.recv()
                    if message == "no_connection":
                        continue
                    elif message == "pong":
                        await pong_queue.put("pong")
                        continue

                    data = json.loads(message)

                    match data:
                        case {"sessionId": _, "sessionSecret": _}:
                            try:
                                session_payload = SessionPayload(**data)
                                handle_session_payload(
                                    session_payload, api_key, expose_url, datadir
                                )
                            except ValidationError as e:
                                if not session_payload:
                                    log.error("Expose session initialization failed", e)
                                    continue
                                pass
                        case _:
                            try:
                                body_payload = BodyPayload(**data)
                                response = handle_body_payload(
                                    body_payload, api_key, f"http://{host}:{port}"
                                )
                                await ws.send(response)
                            except ValidationError as e:
                                log.error("Expose request validation failed", e)
                                continue
            except websockets.exceptions.ConnectionClosedError:
                retries += 1
                log.info(f"Reconnecting to expose server ({retries}/{max_retries})")
                await asyncio.sleep(retry_delay * retries)
                continue
            except socket.gaierror:
                log.info("No internet connection")
            finally:
                ping_task.cancel()
                try:
                    await ping_task
                except asyncio.CancelledError as e:
                    print(e)
                    pass
        else:
            log.info("Expose server connection closed")

    task = asyncio.create_task(listen_for_requests())
    await task  # Wait for listen_for_requests to complete


def main(parent_pid, port, verbose, host, expose_url, datadir, api_key, expose_session):
    logging.basicConfig(
        level=logging.DEBUG if verbose.count("v") > 0 else logging.INFO,
        format="%(message)s",
        datefmt="[%X]",
    )

    exit_when_pid_exists(int(parent_pid))
    try:
        asyncio.run(
            expose_server(
                port=int(port),
                host=host,
                expose_url=expose_url,
                datadir=datadir,
                api_key=api_key if api_key != "None" else None,
                expose_session=expose_session if expose_session != "None" else None,
            )
        )
    except KeyboardInterrupt:
        pass


if __name__ == "__main__":
    main(*sys.argv[1:])
