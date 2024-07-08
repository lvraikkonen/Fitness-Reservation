from sqlalchemy.orm import Session
from sqlalchemy import func, desc, case
from datetime import datetime
from app.models.reservation import Reservation
from app.models.reservation_time_slot import ReservationTimeSlot
from app.models.user import User
from app.models.venue import Venue
from app.models.facility import Facility
from app.models.feedback import Feedback
from app.schemas.stats import (
    UserReservationStats,
    UserReservationCount,
    UserActivityStats,
    VenueUsageStats,
    VenueUsageCount,
    VenueFeedbackStats,
    FacilityUsageStats,
    FacilityUsageCount
)


class StatsService:
    def __init__(self, db: Session):
        self.db = db

    def get_user_reservation_stats(self, start_date: datetime, end_date: datetime):
        query = self.db.query(
            User.id,
            User.username,
            func.count(Reservation.id).label("reservation_count")
        ).join(Reservation, User.id == Reservation.user_id)

        if start_date:
            query = query.filter(Reservation.created_at >= start_date)
        if end_date:
            query = query.filter(Reservation.created_at <= end_date)

        results = query.group_by(User.id, User.username).all()

        user_reservations = [
            UserReservationCount(user_id=r[0], username=r[1], reservation_count=r[2])
            for r in results
        ]
        total_reservations = sum(r.reservation_count for r in user_reservations)

        stats = UserReservationStats(
            total_reservations=total_reservations,
            user_reservations=user_reservations
        )

        return stats

    def get_user_activity_stats(self, threshold: int):
        user_reservation_counts = self.db.query(
            User.id,
            User.username,
            func.count(Reservation.id).label("reservation_count")
        ).outerjoin(Reservation, User.id == Reservation.user_id) \
            .group_by(User.id, User.username).all()

        active_users = [
            UserReservationCount(user_id=r[0], username=r[1], reservation_count=r[2])
            for r in user_reservation_counts if r[2] >= threshold
        ]

        inactive_users = [
            UserReservationCount(user_id=r[0], username=r[1], reservation_count=r[2])
            for r in user_reservation_counts if r[2] < threshold
        ]

        total_users = len(active_users) + len(inactive_users)

        stats = UserActivityStats(
            total_users=total_users,
            active_users=active_users,
            inactive_users=inactive_users
        )

        return stats

    def get_venue_usage_stats(self, start_date: datetime, end_date: datetime):
        query = (self.db.query(
            Venue.id,
            Venue.name,
            func.count(Reservation.id).label("reservation_count")
        ).join(ReservationTimeSlot, Venue.id == ReservationTimeSlot.venue_id).
                 join(Reservation, ReservationTimeSlot.id == Reservation.time_slot_id))

        if start_date:
            query = query.filter(Reservation.created_at >= start_date)
        if end_date:
            query = query.filter(Reservation.created_at <= end_date)

        results = query.group_by(Venue.id, Venue.name).all()

        venue_usage = [
            VenueUsageCount(venue_id=r[0], venue_name=r[1], reservation_count=r[2])
            for r in results
        ]

        total_venues = self.db.query(Venue).count()

        stats = VenueUsageStats(
            total_venues=total_venues,
            venue_usage=venue_usage
        )

        return stats

    def get_venue_feedback_stats(self):
        total_feedbacks = self.db.query(Feedback).count()

        avg_rating = self.db.query(func.avg(Feedback.rating)) \
            .filter(Feedback.rating != None).scalar()

        venue_ratings = self.db.query(
            Venue.id,
            Venue.name,
            func.avg(Feedback.rating).label("avg_rating"),
            func.count(Feedback.id).label("feedback_count")
        ).join(Feedback, Venue.id == Feedback.venue_id, isouter=True) \
            .group_by(Venue.id, Venue.name).all()

        venue_ratings = [
            {
                "venue_id": vr[0],
                "venue_name": vr[1],
                "avg_rating": float(vr[2]) if vr[2] else 0,
                "feedback_count": vr[3]
            }
            for vr in venue_ratings
        ]

        stats = VenueFeedbackStats(
            total_feedbacks=total_feedbacks,
            avg_rating=avg_rating,
            venue_ratings=venue_ratings
        )

        return stats

    def get_facility_usage_stats(self):
        total_facilities = self.db.query(Facility).count()

        facility_usage = (((self.db.query(
            Facility.id,
            Facility.name,
            func.count(Reservation.id).label("usage_count")
        ).join(Venue, Facility.venue_id == Venue.id)
                          .join(ReservationTimeSlot, Venue.id == ReservationTimeSlot.venue_id))
                          .join(Reservation, ReservationTimeSlot.id == Reservation.time_slot_id))
                          .group_by(Facility.id, Facility.name)).all()

        facility_usage = [
            FacilityUsageCount(facility_id=fu[0], facility_name=fu[1], usage_count=fu[2])
            for fu in facility_usage
        ]

        stats = FacilityUsageStats(
            total_facilities=total_facilities,
            facility_usage=facility_usage
        )

        return stats
