from typing import List
from sqlalchemy.orm import Session
from fastapi import Depends, HTTPException

from app.models.reservation import ReservationStatus, Reservation
from app.models.sport_venue import SportVenue
from app.models.venue import Venue, VenueStatus
from app.models.facility import Facility
from app.models.leader_reserved_time import LeaderReservedTime
from app.models.reservation_time_slot import ReservationTimeSlot
from app.schemas.venue import VenueCreate, VenueUpdate
from app.deps import get_db


class VenueService:
    def __init__(self, db: Session = Depends(get_db)):
        self.db = db

    def get_venue(self, venue_id: int) -> Venue:
        venue = self.db.query(Venue).filter(Venue.id == venue_id).first()
        if not venue:
            raise HTTPException(status_code=404, detail="Venue not found")
        return venue

    def get_venues(self, sport_venue_id: int = None, skip: int = 0, limit: int = 100) -> List[Venue]:
        query = self.db.query(Venue)
        if sport_venue_id:
            query = query.filter(Venue.sport_venue_id == sport_venue_id)
        return query.offset(skip).limit(limit).all()

    def create_venue(self, venue: VenueCreate):
        # 检查对应的运动场馆是否存在
        db_sport_venue = self.db.query(SportVenue).filter(SportVenue.id == venue.sport_venue_id).first()
        if db_sport_venue:
            db_venue = Venue(**venue.dict())
            self.db.add(db_venue)
            self.db.commit()
            self.db.refresh(db_venue)
            return db_venue
        else:
            raise ValueError(f"SportVenue with id {venue.sport_venue_id} does not exist.")

    def update_venue(self, venue_id: int, venue: VenueUpdate) -> Venue:
        db_venue = self.get_venue(venue_id)
        update_data = venue.dict(exclude_unset=True)
        for key, value in update_data.items():
            setattr(db_venue, key, value)
        self.db.commit()
        self.db.refresh(db_venue)
        return db_venue

    def update_venue_status(self, venue_id: int, status: VenueStatus):
        venue = self.db.query(Venue).filter(Venue.id == venue_id).first()
        if venue:
            venue.status = status
            if status == VenueStatus.CLOSED or status == VenueStatus.MAINTENANCE:
                # 取消或重新安排相关的预约
                self.db.query(Reservation).filter(Reservation.time_slot_id.in_(
                    self.db.query(ReservationTimeSlot.id).filter(ReservationTimeSlot.venue_id == venue_id)
                )).update({"status": ReservationStatus.CANCELLED})
            self.db.commit()
            self.db.refresh(venue)
        return venue

    def set_venue_maintenance(self, venue_id: int):
        venue = self.db.query(Venue).filter(Venue.id == venue_id).first()
        if venue:
            venue.status = VenueStatus.MAINTENANCE
            # 取消或重新安排相关的预约
            self.db.query(Reservation).filter(Reservation.time_slot_id.in_(
                self.db.query(ReservationTimeSlot.id).filter(ReservationTimeSlot.venue_id == venue_id)
            )).update({"status": ReservationStatus.CANCELLED})
            self.db.commit()
            self.db.refresh(venue)
        return venue

    def delete_venue(self, venue_id: int):
        db_venue = self.db.query(Venue).filter(Venue.id == venue_id).first()
        if db_venue:
            # 删除关联的设施、预约时间段和领导预留时间
            self.db.query(Facility).filter(Facility.venue_id == venue_id).delete()
            self.db.query(ReservationTimeSlot).filter(ReservationTimeSlot.venue_id == venue_id).delete()
            self.db.query(LeaderReservedTime).filter(LeaderReservedTime.venue_id == venue_id).delete()
            self.db.delete(db_venue)
            self.db.commit()
        return db_venue
