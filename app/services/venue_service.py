from typing import List, Optional
from sqlalchemy.orm import Session
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy import func
from datetime import date, time, timedelta

from app.models.reservation import ReservationStatus, Reservation
from app.models.sport_venue import SportVenue
from app.models.venue import Venue, VenueStatus
from app.models.venue_available_time_slot import VenueAvailableTimeSlot
from app.models.facility import Facility
from app.models.leader_reserved_time import LeaderReservedTime
from app.schemas.venue import VenueCreate, VenueUpdate, VenueStats
from app.schemas.venue_available_time_slot import VenueAvailabilityRead, TimeSlotAvailability
from app.core.config import get_logger
from app.core.exceptions import (VenueNotFoundError, SportVenueNotFoundError,
                                 VenueCreateError, VenueUpdateError, VenueDeleteError)

logger = get_logger(__name__)


class VenueService:
    def __init__(self, db: Session):
        self.db = db

    def get_venue(self, venue_id: int) -> Venue:
        venue = self.db.query(Venue).filter(Venue.id == venue_id).first()
        if not venue:
            raise VenueNotFoundError("Venue not found", status_code=404)
        return venue

    def get_venues(self, sport_venue_id: Optional[int] = None, skip: int = 0, limit: int = 100) -> List[Venue]:
        query = self.db.query(Venue)
        if sport_venue_id:
            query = query.filter(Venue.sport_venue_id == sport_venue_id)
        return query.offset(skip).limit(limit).all()

    def create_venue(self, venue: VenueCreate) -> Venue:
        try:
            db_sport_venue = self.db.query(SportVenue).filter(SportVenue.id == venue.sport_venue_id).first()
            if not db_sport_venue:
                raise SportVenueNotFoundError(f"SportVenue with id {venue.sport_venue_id} does not exist.")

            db_venue = Venue(**venue.dict())
            self.db.add(db_venue)
            self.db.commit()
            self.db.refresh(db_venue)
            return db_venue
        except SQLAlchemyError as e:
            self.db.rollback()
            logger.error(f"Database error occurred while creating venue: {str(e)}")
            raise VenueCreateError(f"Failed to create venue: {str(e)}")

    def update_venue(self, venue_id: int, venue: VenueUpdate) -> Venue:
        try:
            db_venue = self.get_venue(venue_id)
            update_data = venue.dict(exclude_unset=True)
            for key, value in update_data.items():
                setattr(db_venue, key, value)
            self.db.commit()
            self.db.refresh(db_venue)
            return db_venue
        except SQLAlchemyError as e:
            self.db.rollback()
            logger.error(f"Database error occurred while updating venue: {str(e)}")
            raise VenueUpdateError(f"Failed to update venue: {str(e)}")

    def update_venue_status(self, venue_id: int, status: VenueStatus) -> Venue:
        try:
            venue = self.get_venue(venue_id)
            venue.status = status
            if status in [VenueStatus.CLOSED, VenueStatus.MAINTENANCE]:
                self.db.query(Reservation).filter(Reservation.venue_id == venue_id).update(
                    {"status": ReservationStatus.CANCELLED})
            self.db.commit()
            self.db.refresh(venue)
            return venue
        except SQLAlchemyError as e:
            self.db.rollback()
            logger.error(f"Database error occurred while updating venue status: {str(e)}")
            raise VenueUpdateError(f"Failed to update venue status: {str(e)}")

    def set_venue_maintenance(self, venue_id: int) -> Venue:
        return self.update_venue_status(venue_id, VenueStatus.MAINTENANCE)

    def delete_venue(self, venue_id: int) -> None:
        try:
            db_venue = self.get_venue(venue_id)
            self.db.query(Facility).filter(Facility.venue_id == venue_id).delete()
            self.db.query(VenueAvailableTimeSlot).filter(VenueAvailableTimeSlot.venue_id == venue_id).delete()
            self.db.query(LeaderReservedTime).filter(LeaderReservedTime.venue_id == venue_id).delete()
            self.db.query(Reservation).filter(Reservation.venue_id == venue_id).update(
                {"status": ReservationStatus.CANCELLED})
            self.db.delete(db_venue)
            self.db.commit()
        except SQLAlchemyError as e:
            self.db.rollback()
            logger.error(f"Database error occurred while deleting venue: {str(e)}")
            raise VenueDeleteError(f"Failed to delete venue: {str(e)}")

    def search_venues(self, query: str, limit: int = 10) -> List[Venue]:
        return self.db.query(Venue).filter(Venue.name.ilike(f"%{query}%")).limit(limit).all()

    def check_venue_availability(self, venue_id: int, start_date: date, end_date: date) -> List[VenueAvailabilityRead]:
        # 检查输入的有效性
        if start_date > end_date:
            raise ValueError("Start date must be before or equal to end date")

        # 获取场馆信息
        venue = self.db.query(Venue).filter(Venue.id == venue_id).first()
        if not venue:
            raise ValueError(f"Venue with id {venue_id} not found")

        availability_list = []

        current_date = start_date
        while current_date <= end_date:
            # 获取当天的所有可用时间段
            time_slots = self.db.query(VenueAvailableTimeSlot).filter(
                VenueAvailableTimeSlot.venue_id == venue_id,
                VenueAvailableTimeSlot.date == current_date
            ).order_by(VenueAvailableTimeSlot.start_time).all()

            # 如果没有预定义的时间段,使用默认的营业时间
            if not time_slots:
                time_slots = VenueService._generate_default_time_slots(venue, current_date)

            # 获取当天的所有有效预约
            reservations = self.db.query(Reservation).filter(
                Reservation.venue_id == venue_id,
                Reservation.venue_available_time_slot_id.in_([slot.id for slot in time_slots]),
                Reservation.status.in_([ReservationStatus.PENDING, ReservationStatus.CONFIRMED])
            ).all()

            # 计算每个时间段的可用容量
            time_slot_availability = []
            for slot in time_slots:
                reserved_count = sum(1 for r in reservations if r.venue_available_time_slot_id == slot.id)
                available_capacity = max(0, slot.capacity - reserved_count)
                time_slot_availability.append(TimeSlotAvailability(
                    start_time=slot.start_time,
                    end_time=slot.end_time,
                    available_capacity=available_capacity,
                    total_capacity=slot.capacity
                ))

            # 创建当天的可用性记录
            availability_list.append(VenueAvailabilityRead(
                date=current_date,
                venue_id=venue_id,
                venue_name=venue.name,
                time_slots=time_slot_availability
            ))

            current_date += timedelta(days=1)

        return availability_list

    @staticmethod
    def _generate_default_time_slots(venue: Venue, slot_date: date) -> List[VenueAvailableTimeSlot]:
        # 生成默认的时间段,例如每小时一个时间段,从上午9点到晚上10点
        default_slots = []
        start_hour = 9  # 假设默认营业时间从9点开始
        end_hour = 22   # 假设默认营业时间到22点结束

        for hour in range(start_hour, end_hour):
            slot = VenueAvailableTimeSlot(
                venue_id=venue.id,
                date=slot_date,
                start_time=time(hour, 0),
                end_time=time(hour + 1, 0),
                capacity=venue.default_capacity
            )
            default_slots.append(slot)

        return default_slots

    def create_venues_batch(self, venues: List[VenueCreate]) -> List[Venue]:
        try:
            db_venues = [Venue(**venue.dict()) for venue in venues]
            self.db.add_all(db_venues)
            self.db.commit()
            for db_venue in db_venues:
                self.db.refresh(db_venue)
            return db_venues
        except SQLAlchemyError as e:
            self.db.rollback()
            logger.error(f"Database error occurred while creating venues batch: {str(e)}")
            raise VenueCreateError(f"Failed to create venues batch: {str(e)}")

    def get_venue_stats(self) -> VenueStats:
        total_venues = self.db.query(func.count(Venue.id)).scalar()
        venues_by_status = self.db.query(Venue.status, func.count(Venue.id)).group_by(Venue.status).all()
        status_counts = {status.name: count for status, count in venues_by_status}
        return VenueStats(total_venues=total_venues, status_counts=status_counts)
