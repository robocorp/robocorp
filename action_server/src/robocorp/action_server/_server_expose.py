import asyncio
import json

import websockets
from fastapi import FastAPI
from pydantic import BaseModel
from xkcdpass import xkcd_password as xp


class SessionPayload(BaseModel):
    sessionId: str
    sessionSecret: str


class BodyPayload(BaseModel):
    requestId: str
    path: str


async def listen_for_requests(app: FastAPI, url: str):
    async with websockets.connect(f"wss://client.{url}") as ws:
        while True:
            message = await ws.recv()

            data = json.loads(message)

            try:
                payload = SessionPayload(**data)
                print(f"🌍 https://{payload.sessionId}.{url}/openapi.json")
                continue
            except Exception:
                pass

            try:
                payload = BodyPayload(**data)

                if payload.path == "/openapi.json":
                    await ws.send(
                        json.dumps(
                            {
                                "requestId": payload.requestId,
                                "response": json.dumps(
                                    app.openapi(),
                                    indent=2,
                                ),
                            }
                        )
                    )
                    continue
            except Exception:
                pass


async def expose_server(app: FastAPI, url: str):
    """
    Exposes the server to the world.
    """
    asyncio.create_task(listen_for_requests(app=app, url=url))
