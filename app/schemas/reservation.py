from pydantic import BaseModel
from datetime import datetime
from app.models.reservation import ReservationStatus


class ReservationBase(BaseModel):
    start_time: datetime
    end_time: datetime


class ReservationCreate(ReservationBase):
    venue_id: int


class ReservationUpdate(BaseModel):
    status: ReservationStatus


class ReservationResponse(ReservationBase):
    id: int
    user_id: int
    venue_id: int
    status: ReservationStatus

    class Config:
        from_attributes = True


class WaitingListCreate(BaseModel):
    reservation_id: int


class WaitingListResponse(BaseModel):
    id: int
    user_id: int
    reservation_id: int

    class Config:
        from_attributes = True
