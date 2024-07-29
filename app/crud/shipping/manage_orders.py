from fastapi import WebSocketDisconnect, WebSocketException, WebSocket
from app.core import web_socket_manager
from app.models import User
from typing import List

# List to store connected WebSocket clients
websocket_connections: List[WebSocket] = []


async def manage_orders_websocket(websocket: WebSocket):
    await web_socket_manager.connect(websocket)
    try:
        while True:
            data = await websocket.receive_text()
            if data == "ping":
                await websocket.send_text("pong")
    except WebSocketDisconnect:
        web_socket_manager.disconnect(websocket)
