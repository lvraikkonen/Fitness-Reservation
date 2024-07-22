from pydantic import BaseModel
from datetime import datetime
from app.schemas.venue_available_time_slot import VenueAvailableTimeSlotRead


class WaitingListBase(BaseModel):
    reservation_id: int
    user_id: int


class WaitingListCreate(WaitingListBase):
    pass


class WaitingListRead(WaitingListBase):
    id: int
    created_at: datetime
    updated_at: datetime
    reservation_time_slot: VenueAvailableTimeSlotRead

    class Config:
        from_attributes = True


class WaitingListReadWithVenueAvailableTimeSlot(BaseModel):
    id: int
    user_id: int
    venue_available_time_slot_id: int
    venue_available_time_slot: VenueAvailableTimeSlotRead
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class WaitingListUpdate(WaitingListBase):
    pass


class WaitingListReadWithReservationTimeSlot(BaseModel):
    id: int
    user_id: int
    reservation_id: int
    reservation_time_slot: VenueAvailableTimeSlotRead
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True
