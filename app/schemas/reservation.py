from pydantic import BaseModel, field_validator
from typing import List, Optional, Dict, Any
from datetime import datetime, date, time
from app.models.reservation import ReservationStatus


class ReservationCreate(BaseModel):
    user_id: int
    venue_id: int
    date: date
    start_time: time
    end_time: time

    @field_validator('date')
    def validate_date(cls, v: date) -> date:
        if v < date.today():
            raise ValueError('Reservation date cannot be in the past')
        return v

    @field_validator('end_time')
    def validate_end_time(cls, v: time, info: Any) -> time:
        start_time = info.data.get('start_time')
        if start_time and v <= start_time:
            raise ValueError('End time must be after start time')
        return v


class ReservationUpdate(BaseModel):
    status: Optional[ReservationStatus] = None


class Reservation(BaseModel):
    id: int
    user_id: int
    time_slot_id: int
    status: ReservationStatus = ReservationStatus.PENDING
    date: date
    start_time: time
    end_time: time
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class ReservationRead(BaseModel):
    id: int
    user_id: int
    time_slot_id: int
    status: ReservationStatus
    date: date
    start_time: time
    end_time: time
    sport_venue_name: str
    venue_name: str

    class Config:
        from_attributes = True


class PaginatedReservationResponse(BaseModel):
    reservations: List[ReservationRead]
    total_count: int
    page: int
    page_size: int


class CalendarTimeSlot(BaseModel):
    id: int
    date: date
    start_time: time
    end_time: time
    reservations: List[ReservationRead] = []

    class Config:
        from_attributes = True


class VenueCalendarResponse(BaseModel):
    venue_id: int
    venue_name: str
    sport_venue_name: str
    calendar_data: Dict[date, List[CalendarTimeSlot]]
    total_count: int
    total_pages: int
    current_page: int
    page_size: int

    class Config:
        from_attributes = True


class ReservationTimeSlotRead(BaseModel):
    id: int
    venue_id: int
    date: date
    start_time: time
    end_time: time

    class Config:
        from_attributes = True
