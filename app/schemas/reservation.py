from pydantic import BaseModel
from typing import List, Optional
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
