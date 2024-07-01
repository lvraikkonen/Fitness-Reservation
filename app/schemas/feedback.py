from pydantic import BaseModel
from typing import Optional
from datetime import datetime


class FeedbackBase(BaseModel):
    title: str
    content: str


class FeedbackCreate(FeedbackBase):
    user_id: int


class FeedbackUpdate(FeedbackBase):
    pass


class Feedback(FeedbackBase):
    id: int
    user_id: int
    reply: Optional[str] = None
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True
