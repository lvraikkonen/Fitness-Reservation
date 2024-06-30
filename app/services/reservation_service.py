from fastapi import HTTPException
from sqlalchemy.orm import Session
from app.models.reservation import Reservation, ReservationStatus, WaitingList
from app.schemas.reservation import ReservationCreate, ReservationUpdate


def get_reservations(db: Session, user_id: int):
    return db.query(Reservation).filter(Reservation.user_id == user_id).all()


def get_reservation(db: Session, reservation_id: int):
    return db.query(Reservation).filter(Reservation.id == reservation_id).first()


def create_reservation(db: Session, reservation: ReservationCreate, user_id: int):
    # 检查该场馆和时间段是否已有其他预约
    conflicting_reservation = db.query(Reservation).filter(
        Reservation.venue_id == reservation.venue_id,
        Reservation.start_time < reservation.end_time,
        Reservation.end_time > reservation.start_time,
        Reservation.status != ReservationStatus.CANCELLED
    ).first()

    if conflicting_reservation:
        # 如果有冲突,自动将用户加入等候列表
        waiting_list = WaitingList(reservation_id=conflicting_reservation.id, user_id=user_id)
        db.add(waiting_list)
        db.commit()
        raise HTTPException(status_code=400, detail="Reservation conflicts with an existing one. Added to waiting list.")

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
        db_reservation.status = ReservationStatus.CANCELLED
        db.commit()

        # 检查等候列表中是否有等候用户
        waiting_user = db.query(WaitingList).filter(WaitingList.reservation_id == reservation_id).first()
        if waiting_user:
            # 如果有等候用户,将预约分配给第一个等候用户
            db_reservation.user_id = waiting_user.user_id
            db_reservation.status = ReservationStatus.PENDING
            db.delete(waiting_user)
            db.commit()
            db.refresh(db_reservation)

            # 发送通知给等候用户
            send_notification(waiting_user.user_id, f"Reservation {reservation_id} is now available and assigned to you.")

    return db_reservation

def send_notification(user_id: int, message: str):
    # 在这里实现发送通知的逻辑,可以是邮件、短信或APP推送等
    pass


def create_waiting_list(db: Session, reservation_id: int, user_id: int):
    db_waiting_list = WaitingList(reservation_id=reservation_id, user_id=user_id)
    db.add(db_waiting_list)
    db.commit()
    db.refresh(db_waiting_list)
    return db_waiting_list
