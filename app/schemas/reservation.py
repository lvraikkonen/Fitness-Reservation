from pydantic import BaseModel, field_validator, Field
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


class ReservationRead(BaseModel):
    id: int
    user_id: int
    venue_id: int
    venue_available_time_slot_id: int
    status: ReservationStatus
    date: date
    actual_start_time: time
    actual_end_time: time
    is_recurring: bool
    venue_name: str

    class Config:
        from_attributes = True


class ReservationDetailRead(BaseModel):
    id: int
    user_id: int
    venue_id: int
    venue_available_time_slot_id: int
    status: ReservationStatus
    date: date
    actual_start_time: time
    actual_end_time: time
    is_recurring: bool
    venue_name: str
    recurring_reservation_id: Optional[int] = None
    created_at: datetime
    updated_at: datetime
    cancelled_at: Optional[datetime] = None
    checked_in_at: Optional[datetime] = None
    sport_venue_name: str
    user_name: str
    venue_available_time_slot_start: time
    venue_available_time_slot_end: time

    class Config:
        from_attributes = True


class PaginatedReservationResponse(BaseModel):
    reservations: List[ReservationDetailRead]
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


class RecurringReservationCreate(BaseModel):
    user_id: int
    venue_id: int
    start_date: date
    end_date: date
    start_time: time
    end_time: time
    recurrence_pattern: RecurrencePattern
    days_of_week: Optional[List[int]] = Field(None, description="Required for weekly pattern. 0 for Monday, 6 for Sunday")
    day_of_month: Optional[int] = Field(None, ge=1, le=31, description="Required for monthly pattern")

    class Config:
        json_schema_extra = {
            "example": {
                "user_id": 1,
                "venue_id": 1,
                "start_date": "2024-07-01",
                "end_date": "2024-12-31",
                "start_time": "09:00:00",
                "end_time": "10:00:00",
                "recurrence_pattern": "weekly",
                "days_of_week": [1, 3, 5]  # Monday, Wednesday, Friday
            }
        }

class RecurringReservationRead(BaseModel):
    id: int
    user_id: int
    venue_id: int
    start_date: date
    end_date: date
    start_time: time
    end_time: time
    recurrence_pattern: RecurrencePattern
    days_of_week: Optional[List[int]]
    day_of_month: Optional[int]
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class RecurringReservationUpdate(BaseModel):
    end_date: Optional[date]
    start_time: Optional[time]
    end_time: Optional[time]
    recurrence_pattern: Optional[RecurrencePattern]
    days_of_week: Optional[List[int]]
    day_of_month: Optional[int]

    class Config:
        json_schema_extra = {
            "example": {
                "end_date": "2025-06-30",
                "start_time": "10:00:00",
                "end_time": "11:00:00",
                "recurrence_pattern": "weekly",
                "days_of_week": [2, 4, 6]  # Tuesday, Thursday, Saturday
            }
        }


class ReservationConfirmationResult(BaseModel):
    reservation_id: int
    status: ReservationStatus
    confirmed_at: datetime
    message: str
