from pydantic import BaseModel, field_validator
from typing import List, Optional, Dict
from datetime import datetime
from app.models.venue import VenueStatus


class VenueBase(BaseModel):
    name: str
    capacity: int
    default_capacity: int
    status: VenueStatus
    sport_type: str  # 新增字段
    description: Optional[str] = None  # 新增字段
    image_url: Optional[str] = None  # 新增字段
    notice: Optional[str] = None

    @field_validator('default_capacity')
    def validate_default_capacity(cls, v, info):
        if 'capacity' in info.data and v > info.data['capacity']:
            raise ValueError('default_capacity must not exceed capacity')
        return v


class VenueCreate(VenueBase):
    sport_venue_id: int


class VenueUpdate(BaseModel):
    name: Optional[str] = None
    capacity: Optional[int] = None
    default_capacity: Optional[int] = None
    status: Optional[VenueStatus] = None
    sport_type: Optional[str] = None  # 新增字段
    description: Optional[str] = None  # 新增字段
    image_url: Optional[str] = None  # 新增字段
    notice: Optional[str] = None

    @field_validator('default_capacity')
    def validate_default_capacity(cls, v, info):
        if 'capacity' in info.data and v is not None and info.data['capacity'] is not None:
            if v > info.data['capacity']:
                raise ValueError('default_capacity must not exceed capacity')
        return v


class VenueRead(BaseModel):
    id: int
    name: str
    capacity: int
    default_capacity: int
    status: VenueStatus
    sport_type: str
    description: Optional[str] = None
    image_url: Optional[str] = None
    notice: Optional[str] = None
    sport_venue_id: int
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class VenueStats(BaseModel):
    total_venues: int
    status_counts: Dict[str, int]
