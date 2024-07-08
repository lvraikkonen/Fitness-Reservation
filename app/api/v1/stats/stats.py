from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from datetime import datetime
from app.models import Reservation, User, Venue
from app.schemas.stats import (UserReservationStats,
                               UserActivityStats,
                               VenueUsageStats,
                               VenueFeedbackStats,
                               FacilityUsageStats)
from app.deps import get_db
from app.services.stats_service import StatsService

router = APIRouter()


@router.get("/user-reservations", response_model=UserReservationStats)
def get_user_reservation_stats(
    start_date: datetime = None,
    end_date: datetime = None,
    db: Session = Depends(get_db)
):
    stats_service = StatsService(db)
    stats = stats_service.get_user_reservation_stats(start_date, end_date)
    return stats


@router.get("/user-activity", response_model=UserActivityStats)
def get_user_activity_stats(
    threshold: int = 10,
    db: Session = Depends(get_db)
):
    stats_service = StatsService(db)
    stats = stats_service.get_user_activity_stats(threshold)
    return stats


@router.get("/venue-usage", response_model=VenueUsageStats)
def get_venue_usage_stats(
    start_date: datetime = None,
    end_date: datetime = None,
    db: Session = Depends(get_db)
):
    stats_service = StatsService(db)
    stats = stats_service.get_venue_usage_stats(start_date, end_date)
    return stats


@router.get("/venue-feedback", response_model=VenueFeedbackStats)
def get_venue_feedback_stats(db: Session = Depends(get_db)):
    stats_service = StatsService(db)
    stats = stats_service.get_venue_feedback_stats()
    return stats


@router.get("/facility-usage", response_model=FacilityUsageStats)
def get_facility_usage_stats(db: Session = Depends(get_db)):
    stats_service = StatsService(db)
    stats = stats_service.get_facility_usage_stats()
    return stats
