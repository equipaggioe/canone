"""The WebSocket of an account."""

from fastapi import APIRouter, WebSocket

from app.dependencies import ClientDep, HandshakeDep
from app.services import websocket

router = APIRouter(tags=["websocket"])


@router.websocket("/websocket")
async def connect(socket: WebSocket, principal: HandshakeDep, caller: ClientDep) -> None:
    """Open the connection of a session, or close it with 4401.

    A browser shows no code of a refused handshake, so it is accepted.
    """
    if principal is None:
        await socket.accept()
        await socket.close(websocket.UNAUTHENTICATED)
        return
    await websocket.serve(socket, principal, caller)
