from sqlalchemy.orm import Session
from app.models.reservation import Reservation, ReservationStatus
from app.schemas.reservation import ReservationCreate, ReservationUpdate


class ReservationService:
    def __init__(self, db: Session):
        self.db = db

    def create_reservation(self, reservation: ReservationCreate):
        db_reservation = Reservation(**reservation.dict())
        self.db.add(db_reservation)
        self.db.commit()
        self.db.refresh(db_reservation)
        return db_reservation

    def get_reservations(self, user_id: int):
        return self.db.query(Reservation).filter(Reservation.user_id == user_id).all()

    def get_reservation(self, reservation_id: int):
        return self.db.query(Reservation).filter(Reservation.id == reservation_id).first()

    def update_reservation(self, reservation_id: int, reservation: ReservationUpdate):
        db_reservation = self.db.query(Reservation).filter(Reservation.id == reservation_id).first()
        if db_reservation:
            update_data = reservation.dict(exclude_unset=True)
            for key, value in update_data.items():
                setattr(db_reservation, key, value)
            self.db.commit()
            self.db.refresh(db_reservation)
        return db_reservation

    def delete_reservation(self, reservation_id: int):
        db_reservation = self.db.query(Reservation).filter(Reservation.id == reservation_id).first()
        if db_reservation:
            self.db.delete(db_reservation)
            self.db.commit()
        return db_reservation

    def cancel_reservation(self, reservation_id: int):
        db_reservation = self.db.query(Reservation).filter(Reservation.id == reservation_id).first()
        if db_reservation:
            db_reservation.status = ReservationStatus.CANCELLED
            self.db.commit()
            self.db.refresh(db_reservation)
        return db_reservation

    def confirm_reservation(self, reservation_id: int):
        db_reservation = self.db.query(Reservation).filter(Reservation.id == reservation_id).first()
        if db_reservation:
            db_reservation.status = ReservationStatus.CONFIRMED
            self.db.commit()
            self.db.refresh(db_reservation)
        return db_reservation
