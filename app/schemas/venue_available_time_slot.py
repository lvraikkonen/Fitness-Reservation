from pydantic import BaseModel, field_validator
from typing import Optional
from datetime import date, time, datetime
from app.services.venue_service import VenueService


class VenueAvailableTimeSlotBase(BaseModel):
    date: date
    start_time: time
    end_time: time
    capacity: int
    venue_id: int

    @field_validator('capacity')
    def validate_capacity(cls, v, info):
        venue_id = info.data.get('venue_id')
        if venue_id:
            venue_service = VenueService()
            venue = venue_service.get_venue(venue_id)
            if venue and v > venue.capacity:
                raise ValueError(f'Capacity cannot exceed venue capacity of {venue.capacity}')
        return v

    @field_validator('end_time')
    def validate_end_time(cls, v, info):
        if 'start_time' in info.data and v <= info.data['start_time']:
            raise ValueError('end_time must be after start_time')
        return v


class VenueAvailableTimeSlotRead(BaseModel):
    id: int
    venue_id: int
    date: date
    start_time: time
    end_time: time
    capacity: int

    class Config:
        from_attributes = True


class VenueAvailableTimeSlotCreate(VenueAvailableTimeSlotBase):
    pass


class VenueAvailableTimeSlotUpdate(BaseModel):
    date: Optional[date] = None
    start_time: Optional[time] = None
    end_time: Optional[time] = None
    capacity: Optional[int] = None

    @field_validator('capacity')
    def validate_capacity(cls, v, info):
        if v is not None:
            # 注意：这里我们无法直接访问 venue_id，因为它不在模型中
            # 我们需要在服务层处理这个验证
            pass
        return v

    @field_validator('end_time')
    def validate_end_time(cls, v, info):
        if v is not None and 'start_time' in info.data and info.data['start_time'] is not None:
            if v <= info.data['start_time']:
                raise ValueError('end_time must be after start_time')
        return v


class VenueAvailableTimeSlotInDB(VenueAvailableTimeSlotBase):
    id: int
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True
