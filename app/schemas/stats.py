from pydantic import BaseModel
from typing import List


class UserReservationCount(BaseModel):
    user_id: int
    username: str
    reservation_count: int


class UserReservationStats(BaseModel):
    total_reservations: int
    user_reservations: List[UserReservationCount]


class UserActivityStats(BaseModel):
    total_users: int
    active_users: List[UserReservationCount]
    inactive_users: List[UserReservationCount]


class VenueUsageCount(BaseModel):
    venue_id: int
    venue_name: str
    reservation_count: int


class VenueUsageStats(BaseModel):
    total_venues: int
    venue_usage: List[VenueUsageCount]


class VenueFeedbackStats(BaseModel):
    total_feedbacks: int
    avg_rating: float
    venue_ratings: List[dict]


class FacilityUsageCount(BaseModel):
    facility_id: int
    facility_name: str
    usage_count: int


class FacilityUsageStats(BaseModel):
    total_facilities: int
    facility_usage: List[FacilityUsageCount]
