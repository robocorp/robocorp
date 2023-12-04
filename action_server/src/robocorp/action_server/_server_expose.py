import websockets
import asyncio
import json


async def listen_for_requests(session_id: str, session_secret: str, url: str):
    async with websockets.connect(
        f"wss://{url}",
        extra_headers={"x-session-id": session_id, "x-session-secret": session_secret},
    ) as websocket:
        while True:
            message = await websocket.recv()
            data = json.loads(message)
            print("THIS IS DATA", data)


async def expose_server(url: str):
    """
    Exposes the server to the world.
    """
    print("🌊 exposing server", url)
    session_id = "your_session_id"
    session_secret = "your_session_secret"
    asyncio.create_task(
        listen_for_requests(
            session_id=session_id, session_secret=session_secret, url=url
        )
    )
