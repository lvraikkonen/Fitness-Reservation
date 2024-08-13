from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime


class FeedbackBase(BaseModel):
    title: str = Field(..., min_length=1, max_length=100)
    content: str = Field(..., min_length=5)
    rating: int = Field(..., ge=1, le=5)


class FeedbackCreate(FeedbackBase):
    user_id: int
    venue_id: int


class FeedbackUpdate(BaseModel):
    title: Optional[str] = Field(None, min_length=1, max_length=100)
    content: Optional[str] = Field(None, min_length=5)
    rating: Optional[int] = Field(None, ge=1, le=5)


class FeedbackRead(FeedbackBase):
    id: int
    user_id: int
    venue_id: int
    reply: Optional[str] = None
    created_at: datetime
    updated_at: datetime
    user_name: str
    venue_name: str

    class Config:
        from_attributes = True


class FeedbackInDB(FeedbackBase):
    id: int
    user_id: int
    venue_id: int
    reply: Optional[str] = None
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class FeedbackPaginatedResponse(BaseModel):
    items: List[FeedbackRead]
    total: int
    page: int
    size: int
