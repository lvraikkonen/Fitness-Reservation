from typing import List
from sqlalchemy.orm import Session
from fastapi import Depends, HTTPException

from app.models.venue import Venue, VenueStatus
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

    def create_venue(self, venue: VenueCreate) -> Venue:
        db_venue = Venue(**venue.dict())
        self.db.add(db_venue)
        self.db.commit()
        self.db.refresh(db_venue)
        return db_venue

    def update_venue(self, venue_id: int, venue: VenueUpdate) -> Venue:
        db_venue = self.get_venue(venue_id)
        update_data = venue.dict(exclude_unset=True)
        for key, value in update_data.items():
            setattr(db_venue, key, value)
        self.db.commit()
        self.db.refresh(db_venue)
        return db_venue

    def delete_venue(self, venue_id: int):
        db_venue = self.get_venue(venue_id)
        self.db.delete(db_venue)
        self.db.commit()
