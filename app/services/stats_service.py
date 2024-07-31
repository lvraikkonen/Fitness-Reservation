from sqlalchemy.orm import Session
from sqlalchemy import func, desc, case, and_, or_
from datetime import datetime, timedelta
from app.models.reservation import Reservation, ReservationStatus
from app.models.venue_available_time_slot import VenueAvailableTimeSlot
from app.models.user import User
from app.models.venue import Venue
from app.models.facility import Facility
from app.models.feedback import Feedback
from app.schemas.stats import (
    UserReservationStats,
    UserReservationCount,
    UserActivityStats,
    VenueUsageStats, VenueUsageCount, VenueFeedbackStats,
    FacilityUsageStats, FacilityUsageCount,
    DashboardStats, ReservationTrendStats
)


class StatsService:
    def __init__(self, db: Session):
        self.db = db

    def get_user_reservation_stats(self, start_date: datetime, end_date: datetime):
        query = self.db.query(
            User.id,
            User.username,
            func.count(Reservation.id).label("reservation_count")
        ).outerjoin(Reservation, and_(User.id == Reservation.user_id,
                                      Reservation.created_at.between(start_date, end_date)))

        results = query.group_by(User.id, User.username).all()

        user_reservations = [
            UserReservationCount(user_id=r[0], username=r[1], reservation_count=r[2])
            for r in results
        ]
        total_reservations = sum(r.reservation_count for r in user_reservations)

        return UserReservationStats(
            total_reservations=total_reservations,
            user_reservations=user_reservations
        )

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
        ).join(VenueAvailableTimeSlot, Venue.id == VenueAvailableTimeSlot.venue_id)
         .join(Reservation, VenueAvailableTimeSlot.id == Reservation.venue_available_time_slot_id)
         .filter(or_(
            Reservation.status == ReservationStatus.CONFIRMED,
            Reservation.status == ReservationStatus.PENDING
        )))

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

        facility_usage = (self.db.query(
            Facility.id,
            Facility.name,
            func.count(Reservation.id).label("usage_count")
        ).join(Venue, Facility.venue_id == Venue.id)
                          .join(VenueAvailableTimeSlot, Venue.id == VenueAvailableTimeSlot.venue_id)
                          .join(Reservation, VenueAvailableTimeSlot.id == Reservation.venue_available_time_slot_id)
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

    def get_dashboard_stats(self):
        """
        获取管理员仪表板的基本统计信息
        """
        total_users = self.db.query(User).count()
        total_venues = self.db.query(Venue).count()
        today = datetime.now().date()
        today_reservations = self.db.query(Reservation).join(VenueAvailableTimeSlot).filter(
            VenueAvailableTimeSlot.date == today
        ).count()

        return DashboardStats(
            total_users=total_users,
            total_venues=total_venues,
            today_reservations=today_reservations
        )

    def get_reservation_trend_stats(self, days: int = 30):
        """
        获取过去一段时间内的预约趋势
        """
        end_date = datetime.now().date()
        start_date = end_date - timedelta(days=days)

        daily_counts = self.db.query(
            func.date(VenueAvailableTimeSlot.date).label('date'),
            func.count(Reservation.id).label('count')
        ).join(Reservation, VenueAvailableTimeSlot.id == Reservation.venue_available_time_slot_id) \
            .filter(VenueAvailableTimeSlot.date.between(start_date, end_date)) \
            .group_by(func.date(VenueAvailableTimeSlot.date)) \
            .order_by(func.date(VenueAvailableTimeSlot.date)) \
            .all()

        return ReservationTrendStats(
            dates=[str(count[0]) for count in daily_counts],
            counts=[count[1] for count in daily_counts]
        )

    def get_top_users(self, limit: int = 10):
        """
        获取预约次数最多的用户
        """
        top_users = self.db.query(
            User.id,
            User.username,
            func.count(Reservation.id).label('reservation_count')
        ).join(Reservation, User.id == Reservation.user_id) \
            .group_by(User.id, User.username) \
            .order_by(desc('reservation_count')) \
            .limit(limit) \
            .all()

        return [UserReservationCount(user_id=user[0], username=user[1], reservation_count=user[2])
                for user in top_users]

    def get_reservation_status_stats(self):
        """
        获取不同预约状态的统计信息
        """
        status_counts = self.db.query(
            Reservation.status,
            func.count(Reservation.id).label('count')
        ).group_by(Reservation.status).all()

        return {status.name: count for status, count in status_counts}
