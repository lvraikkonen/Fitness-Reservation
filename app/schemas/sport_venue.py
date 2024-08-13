from pydantic import BaseModel, Field
from typing import List, Optional
from datetime import datetime


class SportVenueBase(BaseModel):
    name: str
    location: str
    description: Optional[str] = None
    image_url: Optional[str] = None  # 新增字段


class SportVenueCreate(SportVenueBase):
    pass


class SportVenueUpdate(BaseModel):
    name: Optional[str] = None
    location: Optional[str] = None
    description: Optional[str] = None
    image_url: Optional[str] = None  # 新增字段


class SportVenueInDB(SportVenueBase):
    id: int
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class SportVenueRead(SportVenueInDB):
    pass


class SportVenueList(BaseModel):
    items: List[SportVenueRead]
    total: int
