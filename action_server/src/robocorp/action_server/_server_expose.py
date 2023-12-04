import asyncio
import logging
import json
import httpx

import websockets
from fastapi import FastAPI
from fastapi.testclient import TestClient
from pydantic import BaseModel
from ._settings import get_settings

log = logging.getLogger(__name__)


class SessionPayload(BaseModel):
    sessionId: str
    sessionSecret: str


class BodyPayload(BaseModel):
    requestId: str
    path: str
    method: str = "GET"
    body: dict | None = None


def forward_request(client: TestClient, payload: BodyPayload) -> httpx.Response:
    if payload.method == "GET":
        return client.get(payload.path)
    elif payload.method == "POST":
        return client.post(payload.path, json=payload.body)
    elif payload.method == "PUT":
        return client.put(payload.path, json=payload.body)
    elif payload.method == "DELETE":
        return client.delete(payload.path)
    else:
        raise NotImplementedError(f"Method {payload.method} not implemented")


async def expose_server(app: FastAPI):
    """
    Exposes the server to the world.
    """

    settings = get_settings()

    async def listen_for_requests():
        max_retries = 3
        retry_delay = 1
        retries = 0

        session_payload: SessionPayload | None = None
        headers = (
            {
                "x-session-id": session_payload.sessionId,
                "x-session-secret": session_payload.sessionSecret,
            }
            if session_payload
            else {}
        )

        while retries < max_retries:
            try:
                async with websockets.connect(
                    f"wss://client.{settings.expose_url}", extra_headers=headers
                ) as ws:
                    while True:
                        message = await ws.recv()

                        data = json.loads(message)

                        try:
                            session_payload = SessionPayload(**data)
                            log.info(
                                f"🌍 URL: https://{session_payload.sessionId}.{settings.expose_url}/openapi.json"
                            )
                            continue
                        except Exception:
                            pass

                        try:
                            payload = BodyPayload(**data)
                            # might be a bit hacky, but works elegantly
                            client = TestClient(
                                app,
                                base_url=f"http://{settings.address}:{settings.port}",
                            )
                            response = forward_request(client=client, payload=payload)
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

    asyncio.create_task(listen_for_requests())
