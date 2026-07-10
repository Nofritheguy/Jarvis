import asyncio
import json
from typing import Optional
import numpy as np
from contextlib import asynccontextmanager
from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware

from backend.config import PORT
from backend.core.listener import Listener
from backend.core.transcriber import transcribe
from backend.core.brain import think
from backend.core.speaker import speak
from backend.core.memory import get_history

import backend.integrations.google_auth as _gcal
import backend.integrations.spotify_auth as _spotify
import backend.integrations.messenger_session as _messenger

_connections: set[WebSocket] = set()
_main_loop: Optional[asyncio.AbstractEventLoop] = None


async def broadcast(msg: dict):
    dead = set()
    for ws in _connections:
        try:
            await ws.send_json(msg)
        except Exception:
            dead.add(ws)
    _connections.difference_update(dead)


def broadcast_from_thread(msg: dict):
    """Thread-safe broadcast — schedules on the main event loop."""
    if _main_loop and not _main_loop.is_closed():
        asyncio.run_coroutine_threadsafe(broadcast(msg), _main_loop)


async def handle_audio(audio: np.ndarray):
    await broadcast({"type": "state_change", "state": "thinking"})
    text = await asyncio.get_event_loop().run_in_executor(None, transcribe, audio)
    await broadcast({"type": "transcript", "text": text})

    async def on_tool_call(name, args):
        await broadcast({"type": "tool_call", "tool": name, "args": args})

    async def on_tool_result(name, result):
        await broadcast({"type": "tool_result", "tool": name, "result": result})

    response = await think(text, on_tool_call=on_tool_call, on_tool_result=on_tool_result)
    await broadcast({"type": "response", "text": response})
    await broadcast({"type": "state_change", "state": "speaking"})
    await speak(response)
    await broadcast({"type": "state_change", "state": "idle"})


def _sync_handle_audio(audio: np.ndarray):
    if _main_loop and not _main_loop.is_closed():
        asyncio.run_coroutine_threadsafe(handle_audio(audio), _main_loop)


listener: Optional[Listener] = None


@asynccontextmanager
async def lifespan(app: FastAPI):
    global listener, _main_loop
    _main_loop = asyncio.get_event_loop()

    listener = Listener(
        on_audio=_sync_handle_audio,
        on_state=lambda s: broadcast_from_thread({"type": "state_change", "state": s}),
        on_audio_level=lambda l: broadcast_from_thread({"type": "audio_level", "level": l}),
    )
    listener.start()
    yield
    if listener:
        listener.stop()


app = FastAPI(title="Jarvis", lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/health")
async def health():
    return {"status": "ok"}


@app.get("/history")
async def history(limit: int = 50):
    return {"messages": get_history(limit)}


@app.websocket("/ws")
async def websocket_endpoint(ws: WebSocket):
    await ws.accept()
    _connections.add(ws)
    await ws.send_json({"type": "state_change", "state": "idle"})
    try:
        while True:
            data = await ws.receive_text()
            msg = json.loads(data)
            if msg.get("type") == "user_text":
                text = msg.get("text", "").strip()
                if not text:
                    continue
                await broadcast({"type": "transcript", "text": text})
                await broadcast({"type": "state_change", "state": "thinking"})

                async def on_tool_call(name, args):
                    await broadcast({"type": "tool_call", "tool": name, "args": args})

                async def on_tool_result(name, result):
                    await broadcast({"type": "tool_result", "tool": name, "result": result})

                response = await think(text, on_tool_call=on_tool_call, on_tool_result=on_tool_result)
                await broadcast({"type": "response", "text": response})
                await broadcast({"type": "state_change", "state": "speaking"})
                await speak(response)
                await broadcast({"type": "state_change", "state": "idle"})
    except WebSocketDisconnect:
        _connections.discard(ws)
    except Exception as e:
        print(f"[WS ERROR] {e}")
        _connections.discard(ws)


# ─── Integration endpoints ─────────────────────────────────────────────────────

INTEGRATIONS = ["google_calendar", "spotify", "messenger"]


def _get_status(name: str) -> str:
    try:
        if name == "google_calendar":
            return "connected" if _gcal.is_connected() else "disconnected"
        if name == "spotify":
            return "connected" if _spotify.is_connected() else "disconnected"
        if name == "messenger":
            return "connected" if _messenger.is_connected() else "disconnected"
    except Exception:
        return "error"
    return "disconnected"


@app.get("/integrations")
async def list_integrations():
    return [{"name": n, "status": _get_status(n)} for n in INTEGRATIONS]


@app.post("/integrations/{name}/connect")
async def connect_integration(name: str):
    try:
        if name == "google_calendar":
            _gcal.get_calendar_service()
        elif name == "spotify":
            _spotify.get_spotify_client()
        elif name == "messenger":
            _messenger.get_messenger_session()
        else:
            return {"error": f"Unknown integration: {name}"}
        await broadcast({"type": "integration_status", "name": name, "status": "connected"})
        return {"status": "connected"}
    except Exception as ex:
        return {"error": str(ex)}


@app.post("/integrations/{name}/disconnect")
async def disconnect_integration(name: str):
    if name == "google_calendar":
        _gcal.disconnect()
    elif name == "spotify":
        _spotify.disconnect()
    elif name == "messenger":
        _messenger.disconnect()
    await broadcast({"type": "integration_status", "name": name, "status": "disconnected"})
    return {"status": "disconnected"}


@app.get("/integrations/{name}/status")
async def integration_status(name: str):
    return {"name": name, "status": _get_status(name)}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("backend.main:app", host="0.0.0.0", port=PORT, reload=False)
