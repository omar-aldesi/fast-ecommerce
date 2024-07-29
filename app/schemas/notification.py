from typing import Optional

from fastapi import Query
from pydantic import BaseModel


class NotificationResponse(BaseModel):
    id: int
    message: str
    icon_link: str = None
    is_read: bool

    class Config:
        from_attributes = True


class NotificationFilter(BaseModel):
    status: Optional[str] = Query(None, description="Filter notifications by status")
