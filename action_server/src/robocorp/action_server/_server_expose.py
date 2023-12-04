import asyncio
import json

import websockets
from fastapi import FastAPI
from fastapi.testclient import TestClient
from pydantic import BaseModel
from ._settings import get_settings


class SessionPayload(BaseModel):
    sessionId: str
    sessionSecret: str


class BodyPayload(BaseModel):
    requestId: str
    path: str


async def expose_server(app: FastAPI):
    """
    Exposes the server to the world.
    """

    settings = get_settings()

    async def listen_for_requests():
        async with websockets.connect(f"wss://client.{settings.expose_url}") as ws:
            while True:
                message = await ws.recv()

                data = json.loads(message)

                try:
                    payload = SessionPayload(**data)
                    print(
                        f"🌍 https://{payload.sessionId}.{settings.expose_url}/openapi.json"
                    )
                    continue
                except Exception:
                    pass

                try:
                    payload = BodyPayload(**data)

                    # might be a bit hacky, but works elegantly
                    client = TestClient(
                        app, base_url=f"http://{settings.address}:{settings.port}"
                    )
                    response = client.get(payload.path)
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

                except Exception:
                    pass

    asyncio.create_task(listen_for_requests())
