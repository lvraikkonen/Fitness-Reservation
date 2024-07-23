from pydantic import BaseModel
from typing import List, Optional


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


class DashboardStats(BaseModel):
    total_users: int
    total_venues: int
    today_reservations: int


class ReservationTrendStats(BaseModel):
    dates: List[str]
    counts: List[int]


class TopUserStats(BaseModel):
    user_id: int
    username: str
    reservation_count: int


class ReservationStatusStats(BaseModel):
    PENDING: int = 0
    CONFIRMED: int = 0
    CANCELLED: int = 0


# 如果你想要一个包含所有仪表板统计信息的综合模型，可以这样定义：
class ComprehensiveDashboardStats(BaseModel):
    basic_stats: DashboardStats
    reservation_trend: ReservationTrendStats
    top_users: List[TopUserStats]
    reservation_status: ReservationStatusStats
    recent_user_activity: Optional[UserActivityStats] = None
    recent_venue_usage: Optional[VenueUsageStats] = None
