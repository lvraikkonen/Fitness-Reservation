from pydantic import BaseModel
from typing import List
from datetime import date, time, datetime


class ReservationTimeSlotBase(BaseModel):
    date: date
    start_time: time
    end_time: time


class ReservationTimeSlotCreate(ReservationTimeSlotBase):
    venue_id: int
    pass


class ReservationTimeSlotUpdate(ReservationTimeSlotBase):
    pass


class ReservationTimeSlot(ReservationTimeSlotBase):
    id: int
    venue_id: int  
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True
