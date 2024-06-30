from pydantic import BaseModel
from typing import List, Optional
from app.models.venue import VenueStatus


class VenueImageCreate(BaseModel):
    image_url: str


class VenueImageResponse(VenueImageCreate):
    id: int
    venue_id: int

    class Config:
        from_attributes = True


class VenueBase(BaseModel):
    name: str
    location: str
    description: Optional[str] = None
    status: VenueStatus = VenueStatus.OPEN
    max_capacity: int
    open_time: str
    close_time: str


class VenueCreate(VenueBase):
    pass


class VenueUpdate(VenueBase):
    pass


class VenueResponse(VenueBase):
    id: int
    images: List[VenueImageResponse] = []

    class Config:
        from_attributes = True
