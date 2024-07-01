from typing import List
from sqlalchemy.orm import Session
from fastapi import Depends, HTTPException

from app.models.sport_venue import SportVenue
from app.schemas.sport_venue import SportVenueCreate, SportVenueUpdate
from app.deps import get_db


class SportVenueService:
    def __init__(self, db: Session = Depends(get_db)):
        self.db = db

    def get_sport_venue(self, sport_venue_id: int) -> SportVenue:
        sport_venue = self.db.query(SportVenue).filter(SportVenue.id == sport_venue_id).first()
        if not sport_venue:
            raise HTTPException(status_code=404, detail="Sport venue not found")
        return sport_venue

    def get_sport_venues(self, skip: int = 0, limit: int = 100) -> List[SportVenue]:
        return self.db.query(SportVenue).offset(skip).limit(limit).all()

    def create_sport_venue(self, sport_venue: SportVenueCreate) -> SportVenue:
        db_sport_venue = SportVenue(**sport_venue.dict())
        self.db.add(db_sport_venue)
        self.db.commit()
        self.db.refresh(db_sport_venue)
        return db_sport_venue

    def update_sport_venue(self, sport_venue_id: int, sport_venue: SportVenueUpdate) -> SportVenue:
        db_sport_venue = self.get_sport_venue(sport_venue_id)
        update_data = sport_venue.dict(exclude_unset=True)
        for key, value in update_data.items():
            setattr(db_sport_venue, key, value)
        self.db.commit()
        self.db.refresh(db_sport_venue)
        return db_sport_venue

    def delete_sport_venue(self, sport_venue_id: int):
        db_sport_venue = self.get_sport_venue(sport_venue_id)
        self.db.delete(db_sport_venue)
        self.db.commit()
