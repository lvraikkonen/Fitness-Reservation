from pydantic import BaseModel
from datetime import datetime
from app.schemas.reservation import ReservationTimeSlotRead


class WaitingListBase(BaseModel):
    reservation_id: int
    user_id: int


class WaitingListCreate(WaitingListBase):
    pass


class WaitingListRead(WaitingListBase):
    id: int
    created_at: datetime
    updated_at: datetime
    reservation_time_slot: ReservationTimeSlotRead

    class Config:
        from_attributes = True


class WaitingListUpdate(WaitingListBase):
    pass


class WaitingList(WaitingListBase):
    id: int
    reservation_id: int
    user_id: int
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class WaitingListReadWithReservationTimeSlot(BaseModel):
    id: int
    user_id: int
    reservation_id: int
    reservation_time_slot: ReservationTimeSlotRead
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True
