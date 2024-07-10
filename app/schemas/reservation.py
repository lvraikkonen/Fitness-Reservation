from pydantic import BaseModel
from typing import List, Optional, Dict
from datetime import datetime, date, time
from app.models.reservation import ReservationStatus


class ReservationBase(BaseModel):
    status: ReservationStatus


class ReservationCreate(ReservationBase):
    user_id: int
    venue_id: int
    date: date
    start_time: time
    end_time: time


class ReservationUpdate(ReservationBase):
    status: Optional[ReservationStatus] = None


class Reservation(ReservationBase):
    id: int
    user_id: int
    time_slot_id: int
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
