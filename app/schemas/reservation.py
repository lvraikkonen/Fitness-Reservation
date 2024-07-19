from pydantic import BaseModel, field_validator
from typing import List, Optional, Dict, Any
from datetime import datetime, date, time
from app.models.reservation import ReservationStatus
from app.models.recurring_reservation import RecurrencePattern


class ReservationBase(BaseModel):
    status: ReservationStatus


class ConflictCheckResult(BaseModel):
    has_conflict: bool
    conflict_reason: Optional[str] = None
    conflicting_slots: List[Dict[str, Any]] = []


class ReservationCreate(ReservationBase):
    user_id: int
    venue_id: int
    date: date
    start_time: time
    end_time: time
    is_recurring: bool = False
    recurring_pattern: Optional[RecurrencePattern] = None
    recurrence_end_date: Optional[date] = None

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
    venue_available_time_slot_id: Optional[int] = None


class ReservationRead(ReservationBase):
    id: int
    user_id: int
    venue_available_time_slot_id: int
    status: ReservationStatus
    date: date
    start_time: time
    end_time: time
    sport_venue_name: str
    venue_name: str
    is_recurring: bool
    recurring_reservation_id: Optional[int]

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
    capacity: int
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


class VenueAvailableTimeSlotRead(BaseModel):
    id: int
    venue_id: int
    date: date
    start_time: time
    end_time: time
    capacity: int

    class Config:
        from_attributes = True
