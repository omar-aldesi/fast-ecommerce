from typing import List

from fastapi import APIRouter, Depends, WebSocket, WebSocketDisconnect
from sqlalchemy.orm import Session

from app.core.deps import get_current_user
from app.crud.notification import active_connections, update_notification_status
from app.db import get_db
from app.models import User
from app.schemas.notification import NotificationResponse, NotificationFilter

router = APIRouter()


@router.get("/list", response_model=List[NotificationResponse])
def list_user_notifications(filter: NotificationFilter = Depends(), user: User = Depends(get_current_user)):
    if filter.status == "unread":
        return [n for n in user.notifications if not n.is_read]
    elif filter.status == "read":
        return [n for n in user.notifications if n.is_read]
    return user.notifications


@router.put("/mark_as_read/{notification_id}")
def mark_notification_as_read(notification_id: int, db: Session = Depends(get_db),
                              user: User = Depends(get_current_user)):
    return update_notification_status(db, notification_id, user)


@router.websocket("/{user_id}")
async def websocket_endpoint(websocket: WebSocket, user_id: int):
    await websocket.accept()
    active_connections[user_id] = websocket
    try:
        while True:
            # Keep the connection alive
            await websocket.receive_text()
    except WebSocketDisconnect:
        del active_connections[user_id]
