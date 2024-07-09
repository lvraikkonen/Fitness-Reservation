from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import Optional, List, Union
from datetime import date
from app.deps import get_db, get_current_user, get_current_admin
from app.models.user import User
from app.services.reservation_service import ReservationService
from app.schemas.reservation import ReservationCreate, ReservationUpdate, ReservationRead
from app.schemas.reservation import VenueCalendarResponse
from app.schemas.waiting_list import WaitingList as WaitingListRead

router = APIRouter()


@router.post("/reservations", response_model=Union[ReservationRead, WaitingListRead])
def create_reservation(
        reservation: ReservationCreate,
        current_user: User = Depends(get_current_user),
        db: Session = Depends(get_db)
):
    reservation_service = ReservationService(db)
    try:
        result = reservation_service.create_reservation(reservation)
        if isinstance(result, dict):
            return ReservationRead(**result)
        else:
            return WaitingListRead.from_orm(result)
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/reservations/{reservation_id}", response_model=ReservationRead)
def get_reservation(
        reservation_id: int,
        current_user: User = Depends(get_current_user),
        db: Session = Depends(get_db)
):
    reservation_service = ReservationService(db)
    reservation = reservation_service.get_reservation(reservation_id)
    if not reservation:
        raise HTTPException(status_code=404, detail="Reservation not found")
    return reservation


@router.put("/reservations/{reservation_id}", response_model=ReservationRead)
def update_reservation(
        reservation_id: int,
        reservation: ReservationUpdate,
        current_user: User = Depends(get_current_user),
        db: Session = Depends(get_db)
):
    reservation_service = ReservationService(db)
    updated_reservation = reservation_service.update_reservation(reservation_id, reservation)
    if not updated_reservation:
        raise HTTPException(status_code=404, detail="Reservation not found")
    return updated_reservation


@router.delete("/reservations/{reservation_id}")
def delete_reservation(
        reservation_id: int,
        current_user: User = Depends(get_current_user),
        db: Session = Depends(get_db)
):
    reservation_service = ReservationService(db)
    deleted = reservation_service.delete_reservation(reservation_id)
    if not deleted:
        raise HTTPException(status_code=404, detail="Reservation not found")
    return {"message": "Reservation deleted successfully"}


@router.post("/reservations/{reservation_id}/confirm")
def confirm_reservation(
        reservation_id: int,
        current_user: User = Depends(get_current_admin),
        db: Session = Depends(get_db)
):
    reservation_service = ReservationService(db)
    try:
        reservation_service.confirm_reservation(reservation_id)
        return {"message": "Reservation confirmed successfully"}
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/venues/{venue_id}/waiting-list", response_model=List[WaitingListRead])
def get_waiting_list(
        venue_id: int,
        current_user: User = Depends(get_current_admin),
        db: Session = Depends(get_db)
):
    reservation_service = ReservationService(db)
    return reservation_service.get_waiting_list(venue_id)


@router.get("/venues/{venue_id}/calendar", response_model=VenueCalendarResponse)
def get_venue_calendar(
    venue_id: int,
    start_date: Optional[date] = None,
    end_date: Optional[date] = None,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    reservation_service = ReservationService(db)
    calendar_data = reservation_service.get_venue_calendar(venue_id, start_date, end_date)
    return calendar_data


@router.get("/reservations/{venue_id}")
def get_venue_reservations(venue_id: int, db: Session = Depends(get_db)):
    reservation_service = ReservationService(db)
    return reservation_service.get_venue_calendar(venue_id)


@router.get("/user-reservations", response_model=List[ReservationRead])
async def get_user_reservations(
    venue_id: Optional[int] = None,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    reservation_service = ReservationService(db)
    reservations = reservation_service.get_user_reservations(current_user.id, venue_id)
    return reservations
