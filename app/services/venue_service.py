from typing import List, Optional
from sqlalchemy.orm import Session
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy import func

from app.models.reservation import ReservationStatus, Reservation
from app.models.sport_venue import SportVenue
from app.models.venue import Venue, VenueStatus
from app.models.venue_available_time_slot import VenueAvailableTimeSlot
from app.models.facility import Facility
from app.models.leader_reserved_time import LeaderReservedTime
from app.schemas.venue import VenueCreate, VenueUpdate, VenueStats
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
