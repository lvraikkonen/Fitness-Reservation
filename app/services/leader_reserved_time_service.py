from sqlalchemy.orm import Session
from app.models.leader_reserved_time import LeaderReservedTime
from app.schemas.leader_reserved_time import LeaderReservedTimeCreate, LeaderReservedTimeUpdate


class LeaderReservedTimeService:
    def __init__(self, db: Session):
        self.db = db

    def create_leader_reserved_time(self, leader_reserved_time: LeaderReservedTimeCreate):
        db_leader_reserved_time = LeaderReservedTime(**leader_reserved_time.dict())
        self.db.add(db_leader_reserved_time)
        self.db.commit()
        self.db.refresh(db_leader_reserved_time)
        return db_leader_reserved_time

    def get_leader_reserved_times(self, venue_id: int):
        return self.db.query(LeaderReservedTime).filter(LeaderReservedTime.venue_id == venue_id).all()

    def get_leader_reserved_time(self, leader_reserved_time_id: int):
        return self.db.query(LeaderReservedTime).filter(LeaderReservedTime.id == leader_reserved_time_id).first()

    def update_leader_reserved_time(self, leader_reserved_time_id: int, leader_reserved_time: LeaderReservedTimeUpdate):
        db_leader_reserved_time = self.db.query(LeaderReservedTime).filter(LeaderReservedTime.id == leader_reserved_time_id).first()
        if db_leader_reserved_time:
            update_data = leader_reserved_time.dict(exclude_unset=True)
            for key, value in update_data.items():
                setattr(db_leader_reserved_time, key, value)
            self.db.commit()
            self.db.refresh(db_leader_reserved_time)
        return db_leader_reserved_time

    def delete_leader_reserved_time(self, leader_reserved_time_id: int):
        db_leader_reserved_time = self.db.query(LeaderReservedTime).filter(LeaderReservedTime.id == leader_reserved_time_id).first()
        if db_leader_reserved_time:
            self.db.delete(db_leader_reserved_time)
            self.db.commit()
        return db_leader_reserved_time
