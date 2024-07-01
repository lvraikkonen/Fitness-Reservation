from typing import List
from sqlalchemy.orm import Session
from fastapi import Depends, HTTPException
from datetime import datetime

from app.models.reservation import Reservation, ReservationStatus
from app.schemas.reservation import ReservationCreate
from app.services.reservation_conflict_service import ReservationConflictService
from app.deps import get_db


class ReservationService:
    def __init__(self, db: Session = Depends(get_db), conflict_service: ReservationConflictService = Depends()):
        self.db = db
        self.conflict_service = conflict_service

    def get_reservation(self, reservation_id: int) -> Reservation:
        reservation = self.db.query(Reservation).filter(Reservation.id == reservation_id).first()
        if not reservation:
            raise HTTPException(status_code=404, detail="Reservation not found")
        return reservation

    def get_reservations(self, user_id: int = None, time_slot_id: int = None, skip: int = 0, limit: int = 100) -> List[Reservation]:
        query = self.db.query(Reservation)
        if user_id:
            query = query.filter(Reservation.user_id == user_id)
        if time_slot_id:
            query = query.filter(Reservation.time_slot_id == time_slot_id)
        return query.offset(skip).limit(limit).all()

    def create_reservation(self, reservation: ReservationCreate) -> Reservation:
        # 检查预约冲突
        if self.conflict_service.check_reservation_conflict(reservation.time_slot_id, reservation.date):
            raise HTTPException(status_code=400, detail="Time slot already reserved")

        db_reservation = Reservation(**reservation.dict())
        self.db.add(db_reservation)
        self.db.commit()
        self.db.refresh(db_reservation)
        return db_reservation

    def update_reservation_status(self, reservation_id: int, status: ReservationStatus) -> Reservation:
        db_reservation = self.get_reservation(reservation_id)
        db_reservation.status = status
        self.db.commit()
        self.db.refresh(db_reservation)
        return db_reservation

    def delete_reservation(self, reservation_id: int):
        db_reservation = self.get_reservation(reservation_id)
        db_reservation.status = ReservationStatus.CANCELLED
        self.db.commit()
        self.db.refresh(db_reservation)
