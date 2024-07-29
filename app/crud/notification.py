from typing import Dict

from sqlalchemy.orm import Session
from fastapi import HTTPException, WebSocket

from app.db.session import SessionLocal
from app.models import Notification, User
from app.db import get_background_task_db

# Store active WebSocket connections
active_connections: Dict[int, WebSocket] = {}


async def create_notification(user_id: int, message: str):
    db = SessionLocal()
    try:
        user = db.query(User).get(user_id)
        if not user:
            raise HTTPException(status_code=404, detail="User not found")
        notification = Notification(message=message, user_id=user_id)
        db.add(notification)
        db.commit()
        db.refresh(notification)

        # Send notification via WebSocket if user is connected
        if user_id in active_connections:
            await send_notification(user_id, notification)

        return notification
    finally:
        db.close()


async def send_notification(user_id: int, notification: Notification):
    if user_id in active_connections:
        websocket = active_connections[user_id]
        await websocket.send_json({
            "id": notification.id,
            "icon": notification.icon,
            "message": notification.message,
            "is_read": notification.is_read
        })


def update_notification_status(db: Session, notification_id, user: User):
    notification = db.query(Notification).get(notification_id)
    if not notification:
        raise HTTPException(status_code=404, detail="Notification not found")
    if notification.user_id != user.id:
        raise HTTPException(status_code=403, detail="You are not authorized to update this notification")
    notification.is_read = True
    db.commit()
