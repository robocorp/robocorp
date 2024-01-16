import asyncio
import codecs
import json
import logging
import os
import sys
from typing import Optional

import requests
import websockets
from pydantic import BaseModel, ValidationError

from robocorp.action_server._robo_utils.process import exit_when_pid_exists

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
    no_connection_queue: asyncio.Queue,
):
    while True:
        await asyncio.sleep(2)
        await ws.send("ping")

        try:
            await asyncio.wait_for(pong_queue.get(), timeout=2)
        except asyncio.TimeoutError:
            log.debug("Ping-pong message timeout")
            await ws.close()
            await no_connection_queue.put("no_connection")
            break


class ExposePingTimeoutError(Exception):
    pass


async def expose_server(
    port: int,
    host: str,
    expose_url: str,
    datadir: str,
    expose_session: str | None = None,
):
    """
    Exposes the server to the world.
    """

    pong_queue: asyncio.Queue = asyncio.Queue(maxsize=1)
    no_connection_queue: asyncio.Queue = asyncio.Queue(maxsize=1)

    async def listen_for_requests() -> None:
        max_retries = 3
        retry_delay = 3
        retries = 0

        session_payload: Optional[SessionPayload] = (
            get_expose_session_payload(expose_session) if expose_session else None
        )
        while retries < max_retries:
            headers = (
                {
                    "x-session-id": session_payload.sessionId,
                    "x-session-secret": session_payload.sessionSecret,
                }
                if session_payload
                else {}
            )

            try:
                async with websockets.connect(
                    f"wss://client.{expose_url}",
                    extra_headers=headers,
                    logger=log,
                    close_timeout=0,
                ) as ws:
                    if retries > 0:
                        log.info("Reconnected to expose tunnel server")
                        retries = 0

                    ping_task = asyncio.create_task(
                        handle_ping_pong(ws, pong_queue, no_connection_queue)
                    )

                    try:
                        while True:
                            done, pending = await asyncio.wait(
                                [ws.recv(), no_connection_queue.get()],
                                return_when=asyncio.FIRST_COMPLETED,
                            )

                            for task in done:
                                message = task.result()
                                if message == "no_connection":
                                    raise ExposePingTimeoutError("No connection")

                            for task in pending:
                                task.cancel()

                            if message == "pong":
                                await pong_queue.put("pong")
                                continue

                            data = json.loads(message)

                            try:
                                session_payload = SessionPayload(**data)

                                url = (
                                    f"https://{session_payload.sessionId}.{expose_url}"
                                )
                                log.info(f"  🌍 Public URL: {url}\n")
                                new_expose_session = get_expose_session(session_payload)
                                write_expose_session_json(
                                    datadir=datadir,
                                    expose_session_json=ExposeSessionJson(
                                        expose_session=new_expose_session,
                                        url=url,
                                    ),
                                )
                                continue
                            except Exception as e:
                                if not session_payload:
                                    log.error(
                                        "Unable to get session payload. Exposing the local server failed. Try again."
                                    )
                                    raise
                                pass

                            try:
                                payload = BodyPayload(**data)
                                base_url = f"http://{host}:{port}"
                                response: requests.Response = forward_request(
                                    base_url=base_url, payload=payload
                                )
                                await ws.send(
                                    json.dumps(
                                        {
                                            "requestId": payload.requestId,
                                            "response": json.dumps(
                                                response.json(),
                                                indent=2,
                                            ),
                                            "status": response.status_code,
                                        }
                                    )
                                )

                            except Exception as e:
                                log.error("Error forwarding request", e)
                                pass

                    except Exception as e:
                        raise e

                    finally:
                        ping_task.cancel()
                        try:
                            await ping_task
                        except asyncio.CancelledError:
                            pass

            except (
                websockets.ConnectionClosed,
                websockets.ConnectionClosedError,
                ExposePingTimeoutError,
                OSError,
            ) as e:
                retries += 1
                log.info(
                    f"Connection closed, attempting to reconnect...({retries}/{max_retries})"
                )
                log.debug(e)
                await asyncio.sleep(retry_delay * retries)

            except Exception as e:
                log.error("Error connecting to expose tunnel server", e)
                break

        else:
            log.error(
                "Could not connect to expose tunnel server. Check your connectivity and try again."
            )

    task = asyncio.create_task(listen_for_requests())
    await task  # Wait for listen_for_requests to complete


def main(parent_pid, port, verbose, host, expose_url, datadir, expose_session):
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
                expose_session=expose_session if expose_session != "None" else None,
            )
        )
    except KeyboardInterrupt:
        pass


if __name__ == "__main__":
    main(*sys.argv[1:])
