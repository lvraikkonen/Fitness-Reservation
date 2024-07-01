from pydantic import BaseModel
from datetime import datetime


class NotificationBase(BaseModel):
    title: str
    content: str
    type: str
    is_read: bool = False


class NotificationCreate(NotificationBase):
    user_id: int


class NotificationUpdate(NotificationBase):
    pass


class Notification(NotificationBase):
    id: int
    user_id: int
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True
