from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime
from app.models.venue import VenueStatus


class VenueBase(BaseModel):
    name: str
    capacity: int
    status: VenueStatus
    notice: Optional[str] = None


class VenueCreate(VenueBase):
    sport_venue_id: int


class VenueUpdate(BaseModel):
    name: Optional[str] = None
    capacity: Optional[int] = None
    status: Optional[VenueStatus] = None
    notice: Optional[str] = None


class Venue(VenueBase):
    id: int
    sport_venue_id: int
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True
