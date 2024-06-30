from sqlalchemy.orm import Session
from app.models.reservation import Reservation, ReservationStatus, WaitingList
from app.schemas.reservation import ReservationCreate, ReservationUpdate


def get_reservations(db: Session, user_id: int):
    return db.query(Reservation).filter(Reservation.user_id == user_id).all()


def get_reservation(db: Session, reservation_id: int):
    return db.query(Reservation).filter(Reservation.id == reservation_id).first()


def create_reservation(db: Session, reservation: ReservationCreate, user_id: int):
    db_reservation = Reservation(**reservation.dict(), user_id=user_id)
    db.add(db_reservation)
    db.commit()
    db.refresh(db_reservation)
    return db_reservation


def update_reservation(db: Session, reservation_id: int, reservation: ReservationUpdate):
    db_reservation = get_reservation(db, reservation_id)
    if db_reservation:
        update_data = reservation.dict(exclude_unset=True)
        for key, value in update_data.items():
            setattr(db_reservation, key, value)
        db.commit()
        db.refresh(db_reservation)
    return db_reservation


def delete_reservation(db: Session, reservation_id: int):
    db_reservation = get_reservation(db, reservation_id)
    if db_reservation:
        db.delete(db_reservation)
        db.commit()
    return db_reservation


def create_waiting_list(db: Session, reservation_id: int, user_id: int):
    db_waiting_list = WaitingList(reservation_id=reservation_id, user_id=user_id)
    db.add(db_waiting_list)
    db.commit()
    db.refresh(db_waiting_list)
    return db_waiting_list
