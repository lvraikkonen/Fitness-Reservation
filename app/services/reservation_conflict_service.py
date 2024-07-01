from sqlalchemy.orm import Session
from fastapi import Depends
from datetime import datetime

from app.models.reservation import Reservation, ReservationStatus
from app.models.leader_reserved_time import LeaderReservedTime
from app.models.reservation_time_slot import ReservationTimeSlot
from app.deps import get_db


class ReservationConflictService:
    def __init__(self, db: Session = Depends(get_db)):
        self.db = db

    def check_reservation_conflict(self, time_slot_id: int, date: datetime) -> bool:
        reservation = self.db.query(Reservation).filter(
            Reservation.time_slot_id == time_slot_id,
            Reservation.status != ReservationStatus.CANCELLED
        ).first()
        if reservation:
            return True

        leader_reserved_time = self.db.query(LeaderReservedTime).filter(
            LeaderReservedTime.venue_id == ReservationTimeSlot.venue_id,
            LeaderReservedTime.day_of_week == date.weekday(),
            LeaderReservedTime.start_time <= ReservationTimeSlot.end_time,
            LeaderReservedTime.end_time >= ReservationTimeSlot.start_time
        ).first()
        if leader_reserved_time:
            return True

        return False
