from typing import List
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError
from fastapi import Depends, HTTPException

from app.models.sport_venue import SportVenue
from app.models.venue import Venue
from app.schemas.sport_venue import SportVenueCreate, SportVenueUpdate
from app.deps import get_db
from app.core.config import get_logger

logger = get_logger(__name__)


class SportVenueService:
    def __init__(self, db: Session = Depends(get_db)):
        self.db = db

    def get_sport_venue(self, sport_venue_id: int) -> SportVenue:
        sport_venue = self.db.query(SportVenue).filter(SportVenue.id == sport_venue_id).first()
        if not sport_venue:
            raise HTTPException(status_code=404, detail="Sport venue not found")
        return sport_venue

    def get_sport_venues(self, skip: int = 0, limit: int = 100, sort_by: str = "name") -> List[SportVenue]:
        return self.db.query(SportVenue).order_by(getattr(SportVenue, sort_by)).offset(skip).limit(limit).all()

    def create_sport_venue(self, sport_venue: SportVenueCreate) -> SportVenue:
        try:
            db_sport_venue = SportVenue(**sport_venue.dict())
            self.db.add(db_sport_venue)
            self.db.commit()
            self.db.refresh(db_sport_venue)
            logger.info(f"Created new sport venue: {db_sport_venue.name}")
            return db_sport_venue
        except IntegrityError:
            self.db.rollback()
            raise HTTPException(status_code=400, detail="Sport venue with this name already exists")

    def update_sport_venue(self, sport_venue_id: int, sport_venue: SportVenueUpdate) -> SportVenue:
        db_sport_venue = self.get_sport_venue(sport_venue_id)
        try:
            update_data = sport_venue.dict(exclude_unset=True)
            for key, value in update_data.items():
                setattr(db_sport_venue, key, value)
            self.db.commit()
            self.db.refresh(db_sport_venue)
            logger.info(f"Updated sport venue: {db_sport_venue.name}")
            return db_sport_venue
        except IntegrityError:
            self.db.rollback()
            raise HTTPException(status_code=400, detail="Update failed due to constraint violation")

    def delete_sport_venue(self, sport_venue_id: int):
        db_sport_venue = self.get_sport_venue(sport_venue_id)
        try:
            # 开始事务
            self.db.begin_nested()

            # 删除关联的具体场馆
            self.db.query(Venue).filter(Venue.sport_venue_id == sport_venue_id).delete()

            # 删除运动场馆
            self.db.delete(db_sport_venue)

            self.db.commit()
            logger.info(f"Deleted sport venue: {db_sport_venue.name}")
            return db_sport_venue
        except Exception as e:
            self.db.rollback()
            logger.error(f"Failed to delete sport venue: {str(e)}")
            raise HTTPException(status_code=500, detail="Failed to delete sport venue")

    def get_venues_by_sport_venue(self, sport_venue_id: int) -> List[Venue]:
        sport_venue = self.get_sport_venue(sport_venue_id)
        return sport_venue.venues

    def search_sport_venues(self, query: str, limit: int = 10) -> List[SportVenue]:
        return self.db.query(SportVenue).filter(
            SportVenue.name.ilike(f"%{query}%") | SportVenue.location.ilike(f"%{query}%")
        ).limit(limit).all()
