from typing import List
from sqlalchemy.orm import Session
from fastapi import HTTPException

from app.models.facility import Facility
from app.models.venue import Venue
from app.schemas.facility import FacilityCreate, FacilityUpdate
from app.core.config import get_logger

logger = get_logger(__name__)


class FacilityService:
    def __init__(self, db: Session):
        self.db = db

    def get_facility(self, facility_id: int) -> Facility:
        facility = self.db.query(Facility).filter(Facility.id == facility_id).first()
        if not facility:
            raise HTTPException(status_code=404, detail="Facility not found")
        return facility

    def get_facilities(self, venue_id: int = None, skip: int = 0, limit: int = 100) -> List[Facility]:
        query = self.db.query(Facility)
        if venue_id:
            query = query.filter(Facility.venue_id == venue_id)
        return query.offset(skip).limit(limit).all()

    def create_facility(self, venue_id: int, facility: FacilityCreate):
        # 检查对应的具体场馆是否存在
        db_venue = self.db.query(Venue).filter(Venue.id == venue_id).first()
        if db_venue:
            db_facility = Facility(**facility.dict(), venue_id=venue_id)
            self.db.add(db_facility)
            self.db.commit()
            self.db.refresh(db_facility)
            return db_facility
        else:
            raise ValueError(f"Venue with id {venue_id} does not exist.")

    def update_facility(self, facility_id: int, facility: FacilityUpdate) -> Facility:
        db_facility = self.get_facility(facility_id)
        update_data = facility.dict(exclude_unset=True)
        for key, value in update_data.items():
            setattr(db_facility, key, value)
        self.db.commit()
        self.db.refresh(db_facility)
        return db_facility

    def delete_facility(self, facility_id: int):
        db_facility = self.get_facility(facility_id)
        self.db.delete(db_facility)
        self.db.commit()
