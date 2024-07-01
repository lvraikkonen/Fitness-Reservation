from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime
from app.models.reservation import ReservationStatus


class ReservationBase(BaseModel):
    status: ReservationStatus


class ReservationCreate(ReservationBase):
    user_id: int
    time_slot_id: int


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
