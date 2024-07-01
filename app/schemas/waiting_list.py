from pydantic import BaseModel
from datetime import datetime


class WaitingListBase(BaseModel):
    pass


class WaitingListCreate(WaitingListBase):
    reservation_id: int
    user_id: int


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
