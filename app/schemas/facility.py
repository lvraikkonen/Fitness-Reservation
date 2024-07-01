from pydantic import BaseModel
from typing import Optional
from datetime import datetime


class FacilityBase(BaseModel):
    name: str
    description: Optional[str] = None


class FacilityCreate(FacilityBase):
    venue_id: int
    pass


class FacilityUpdate(FacilityBase):
    name: str
    description: Optional[str] = None


class Facility(FacilityBase):
    id: int
    venue_id: int
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True
