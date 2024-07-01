from pydantic import BaseModel
from datetime import time, datetime


class LeaderReservedTimeBase(BaseModel):
    day_of_week: int
    start_time: time
    end_time: time


class LeaderReservedTimeCreate(LeaderReservedTimeBase):
    user_id: int
    venue_id: int


class LeaderReservedTimeUpdate(LeaderReservedTimeBase):
    pass


class LeaderReservedTime(LeaderReservedTimeBase):
    id: int
    user_id: int
    venue_id: int
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True
