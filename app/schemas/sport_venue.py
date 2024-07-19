from pydantic import BaseModel, Field
from typing import List, Optional
from datetime import datetime


class SportVenueBase(BaseModel):
    name: str
    location: str
    description: Optional[str] = None
    capacity: Optional[int] = Field(None, ge=0)


class SportVenueCreate(SportVenueBase):
    pass


class SportVenueUpdate(BaseModel):
    name: Optional[str] = None
    location: Optional[str] = None
    description: Optional[str] = None
    capacity: Optional[int] = Field(None, ge=0)


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


# 如果需要简化版的 SportVenue 模型（不包含时间戳），可以保留这个
class SportVenue(SportVenueBase):
    id: int

    class Config:
        from_attributes = True