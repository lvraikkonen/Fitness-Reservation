from typing import List
from sqlalchemy.orm import Session
from fastapi import Depends, HTTPException

from app.models.leader_reserved_time import LeaderReservedTime
from app.schemas.leader_reserved_time import LeaderReservedTimeCreate
from app.deps import get_db


class LeaderReservedTimeService:
    def __init__(self, db: Session = Depends(get_db)):
        self.db = db

    def get_leader_reserved_time(self, reserved_time_id: int) -> LeaderReservedTime:
        reserved_time = self.db.query(LeaderReservedTime).filter(LeaderReservedTime.id == reserved_time_id).first()
        if not reserved_time:
            raise HTTPException(status_code=404, detail="Leader reserved time not found")
        return reserved_time

    def get_leader_reserved_times(self, user_id: int = None, venue_id: int = None, skip: int = 0, limit: int = 100) -> List[LeaderReservedTime]:
        query = self.db.query(LeaderReservedTime)
        if user_id:
            query = query.filter(LeaderReservedTime.user_id == user_id)
        if venue_id:
            query = query.filter(LeaderReservedTime.venue_id == venue_id)
        return query.offset(skip).limit(limit).all()

    def create_leader_reserved_time(self, reserved_time: LeaderReservedTimeCreate) -> LeaderReservedTime:
        db_reserved_time = LeaderReservedTime(**reserved_time.dict())
        self.db.add(db_reserved_time)
        self.db.commit()
        self.db.refresh(db_reserved_time)
        return db_reserved_time

    def delete_leader_reserved_time(self, reserved_time_id: int):
        db_reserved_time = self.get_leader_reserved_time(reserved_time_id)
        self.db.delete(db_reserved_time)
        self.db.commit()
