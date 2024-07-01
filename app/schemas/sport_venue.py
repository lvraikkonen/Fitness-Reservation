from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime


class SportVenueBase(BaseModel):
    name: str
    location: str


class SportVenueCreate(SportVenueBase):
    pass


class SportVenueUpdate(BaseModel):
    name: Optional[str] = None
    location: Optional[str] = None


class SportVenue(SportVenueBase):
    id: int
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True
