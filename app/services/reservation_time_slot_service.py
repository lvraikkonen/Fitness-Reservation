from typing import List
from sqlalchemy.orm import Session
from fastapi import Depends, HTTPException
from datetime import datetime

from app.models.reservation_time_slot import ReservationTimeSlot
from app.schemas.reservation_time_slot import ReservationTimeSlotCreate
from app.deps import get_db


class ReservationTimeSlotService:
    def __init__(self, db: Session = Depends(get_db)):
        self.db = db

    def get_time_slot(self, time_slot_id: int) -> ReservationTimeSlot:
        time_slot = self.db.query(ReservationTimeSlot).filter(ReservationTimeSlot.id == time_slot_id).first()
        if not time_slot:
            raise HTTPException(status_code=404, detail="Time slot not found")
        return time_slot

    def get_time_slots(self, venue_id: int = None, date: datetime = None, skip: int = 0, limit: int = 100) -> List[ReservationTimeSlot]:
        query = self.db.query(ReservationTimeSlot)
        if venue_id:
            query = query.filter(ReservationTimeSlot.venue_id == venue_id)
        if date:
            query = query.filter(ReservationTimeSlot.date == date)
        return query.offset(skip).limit(limit).all()

    def create_time_slot(self, time_slot: ReservationTimeSlotCreate) -> ReservationTimeSlot:
        db_time_slot = ReservationTimeSlot(**time_slot.dict())
        self.db.add(db_time_slot)
        self.db.commit()
        self.db.refresh(db_time_slot)
        return db_time_slot

    def delete_time_slot(self, time_slot_id: int):
        db_time_slot = self.get_time_slot(time_slot_id)
        self.db.delete(db_time_slot)
        self.db.commit()
