import asyncio
import json
import logging
import sys
from typing import Optional

import requests
import websockets
from pydantic import BaseModel

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


def forward_request(base_url: str, payload: BodyPayload) -> requests.Response:
    url = base_url.rstrip("/") + "/" + payload.path.lstrip("/")

    if payload.method == "GET":
        return requests.get(url)
    elif payload.method == "POST":
        return requests.post(url, json=payload.body)
    elif payload.method == "PUT":
        return requests.put(url, json=payload.body)
    elif payload.method == "DELETE":
        return requests.delete(url)
    else:
        raise NotImplementedError(f"Method {payload.method} not implemented")


async def expose_server(port: int, host: str, expose_url: str):
    """
    Exposes the server to the world.
    """

    async def listen_for_requests():
        max_retries = 3
        retry_delay = 1
        retries = 0

        session_payload: Optional[SessionPayload] = None
        while retries < max_retries:
            try:
                headers = (
                    {
                        "x-session-id": session_payload.sessionId,
                        "x-session-secret": session_payload.sessionSecret,
                    }
                    if session_payload
                    else {}
                )

                async with websockets.connect(
                    f"wss://client.{expose_url}",
                    extra_headers=headers,
                    logger=log,
                ) as ws:
                    while True:
                        message = await ws.recv()

                        data = json.loads(message)

                        try:
                            session_payload = SessionPayload(**data)
                            log.info(
                                f"🌍 URL: https://{session_payload.sessionId}.{expose_url}"
                            )
                            continue
                        except Exception:
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
                                    }
                                )
                            )

                        except Exception as e:
                            log.error("Error forwarding request", e)
                            pass
            except websockets.exceptions.ConnectionClosed:
                log.info("Connection closed, attempting to reconnect...")
                retries += 1
                # sleep with exponential backoff
                await asyncio.sleep(retry_delay * retries)
            except Exception as e:
                log.error(f"An error occurred: {e}")
                break

    task = asyncio.create_task(listen_for_requests())
    await task  # Wait for listen_for_requests to complete


if __name__ == "__main__":
    parent_pid, port, verbose, host, expose_url = sys.argv[1:]

    logging.basicConfig(
        level=logging.DEBUG if verbose.count("v") > 0 else logging.INFO,
        format="%(message)s",
        datefmt="[%X]",
    )

    exit_when_pid_exists(int(parent_pid))
    asyncio.run(expose_server(port=int(port), host=host, expose_url=expose_url))
