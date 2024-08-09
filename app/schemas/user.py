from pydantic import BaseModel, EmailStr
from typing import List, Optional
from datetime import datetime, date, time
from app.models.reservation import ReservationStatus


class UserBase(BaseModel):
    username: str
    email: EmailStr
    phone: str
    role: int = 0
    is_leader: bool = False
    full_name: Optional[str] = None
    department: Optional[str] = None
    preferred_sports: Optional[str] = None
    preferred_time: Optional[str] = None


class UserCreate(UserBase):
    password: str


class UserUpdate(BaseModel):
    username: Optional[str] = None
    email: Optional[str] = None
    phone: Optional[str] = None
    role: Optional[int] = None
    is_leader: Optional[bool] = None
    full_name: Optional[str] = None
    department: Optional[str] = None
    preferred_sports: Optional[str] = None
    preferred_time: Optional[str] = None


class UserResponse(UserBase):
    id: int

    class Config:
        from_attributes = True


class User(UserBase):
    id: int
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class UserResetPasswordRequest(BaseModel):
    email: EmailStr


class UserResetPassword(BaseModel):
    token: str
    new_password: str


class UpcomingReservation(BaseModel):
    id: int
    venue_name: str
    sport_venue_name: str
    date: date
    start_time: time
    end_time: time
    status: ReservationStatus


class RecentActivity(BaseModel):
    id: int
    activity_type: str
    timestamp: datetime
    venue_name: str
    sport_venue_name: str
    date: Optional[date]
    start_time: Optional[time]
    end_time: Optional[time]
    status: Optional[ReservationStatus]


class RecommendedVenue(BaseModel):
    id: int
    name: str
    sport_venue_name: str


class UserDashboardResponse(BaseModel):
    username: str
    upcoming_reservations: List[UpcomingReservation]
    recent_activities: List[RecentActivity]
    recommended_venues: List[RecommendedVenue]
    monthly_reservation_count: int
    monthly_reservation_limit: int
