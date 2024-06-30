from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
from app.api.deps import get_db, get_current_user
from models.user import User
from app.schemas.reservation import ReservationCreate, ReservationUpdate, ReservationResponse, WaitingListCreate, WaitingListResponse
from app.services.reservation_service import get_reservations, get_reservation, create_reservation, update_reservation, delete_reservation, create_waiting_list

router = APIRouter()


@router.get("/", response_model=List[ReservationResponse])
def read_reservations(db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    reservations = get_reservations(db, user_id=current_user.id)
    return reservations


@router.post("/", response_model=ReservationResponse)
def create_reservation_endpoint(reservation: ReservationCreate, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    return create_reservation(db, reservation=reservation, user_id=current_user.id)


@router.get("/{reservation_id}", response_model=ReservationResponse)
def read_reservation(reservation_id: int, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    db_reservation = get_reservation(db, reservation_id=reservation_id)
    if db_reservation is None or db_reservation.user_id != current_user.id:
        raise HTTPException(status_code=404, detail="Reservation not found")
    return db_reservation


@router.patch("/{reservation_id}", response_model=ReservationResponse)
def update_reservation_endpoint(reservation_id: int, reservation: ReservationUpdate, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    db_reservation = get_reservation(db, reservation_id=reservation_id)
    if db_reservation is None or db_reservation.user_id != current_user.id:
        raise HTTPException(status_code=404, detail="Reservation not found")
    return update_reservation(db, reservation_id=reservation_id, reservation=reservation)


@router.delete("/{reservation_id}", response_model=ReservationResponse)
def delete_reservation_endpoint(reservation_id: int, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    db_reservation = get_reservation(db, reservation_id=reservation_id)
    if db_reservation is None or db_reservation.user_id != current_user.id:
        raise HTTPException(status_code=404, detail="Reservation not found")
    return delete_reservation(db, reservation_id=reservation_id)


@router.post("/{reservation_id}/waiting-list", response_model=WaitingListResponse)
def create_waiting_list_endpoint(reservation_id: int, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    db_reservation = get_reservation(db, reservation_id=reservation_id)
    if db_reservation is None:
        raise HTTPException(status_code=404, detail="Reservation not found")
    return create_waiting_list(db, reservation_id=reservation_id, user_id=current_user.id)
