from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.deps import get_db, get_current_user, get_current_admin

from app.models.user import User
from app.models.venue import Venue, VenueStatus
from app.schemas.venue import VenueCreate, VenueUpdate
from app.schemas.reservation_time_slot import ReservationTimeSlotCreate, ReservationTimeSlotUpdate
from app.services.venue_service import VenueService
from app.services.reservation_time_slot_service import ReservationTimeSlotService

router = APIRouter()


@router.get("/venues")
def get_venues(db: Session = Depends(get_db)):
    venue_service = VenueService(db)
    venues = venue_service.get_venues()
    return venues


@router.post("/venues")
def create_venue(
        venue: VenueCreate,
        current_user: User = Depends(get_current_admin),
        db: Session = Depends(get_db)
):
    venue_service = VenueService(db)
    created_venue = venue_service.create_venue(venue)
    return created_venue


@router.get("/venues/{venue_id}")
def get_venue(venue_id: int, db: Session = Depends(get_db)):
    venue_service = VenueService(db)
    venue = venue_service.get_venue(venue_id)
    if not venue:
        raise HTTPException(status_code=404, detail="Venue not found")
    return venue


@router.put("/venues/{venue_id}")
def update_venue(
        venue_id: int,
        venue: VenueUpdate,
        current_user: User = Depends(get_current_admin),
        db: Session = Depends(get_db)
):
    venue_service = VenueService(db)
    updated_venue = venue_service.update_venue(venue_id, venue)
    if not updated_venue:
        raise HTTPException(status_code=404, detail="Venue not found")
    return updated_venue


@router.delete("/venues/{venue_id}")
def delete_venue(
        venue_id: int,
        current_user: User = Depends(get_current_admin),
        db: Session = Depends(get_db)
):
    venue_service = VenueService(db)
    deleted_venue = venue_service.delete_venue(venue_id)
    if not deleted_venue:
        raise HTTPException(status_code=404, detail="Venue not found")
    return {"message": "Venue deleted successfully"}


@router.patch("/venues/{venue_id}/status")
def update_venue_status(
        venue_id: int,
        status: VenueStatus,
        current_user: User = Depends(get_current_admin),
        db: Session = Depends(get_db)
):
    venue_service = VenueService(db)
    updated_venue = venue_service.update_venue_status(venue_id, status)
    if not updated_venue:
        raise HTTPException(status_code=404, detail="Venue not found")
    return updated_venue


@router.post("/venues/{venue_id}/maintenance")
def set_venue_maintenance(
        venue_id: int,
        current_user: User = Depends(get_current_admin),
        db: Session = Depends(get_db)
):
    venue_service = VenueService(db)
    result = venue_service.set_venue_maintenance(venue_id)
    if not result:
        raise HTTPException(status_code=404, detail="Venue not found")
    return result


@router.post("/venues/{venue_id}/reservation-time-slots")
def create_reservation_time_slot(
        venue_id: int,
        time_slot: ReservationTimeSlotCreate,
        current_user: User = Depends(get_current_admin),
        db: Session = Depends(get_db)
):
    reservation_time_slot_service = ReservationTimeSlotService(db)
    created_time_slot = reservation_time_slot_service.create_reservation_time_slot(venue_id, time_slot)
    return created_time_slot


@router.get("/venues/{venue_id}/reservation-time-slots")
def get_reservation_time_slots(
        venue_id: int, db: Session = Depends(get_db)
):
    reservation_time_slot_service = ReservationTimeSlotService(db)
    time_slots = reservation_time_slot_service.get_reservation_time_slots(venue_id)
    return time_slots


@router.put("/venues/{venue_id}/reservation-time-slots/{time_slot_id}")
def update_reservation_time_slot(
        venue_id: int,
        time_slot_id: int,
        time_slot: ReservationTimeSlotUpdate,
        current_user: User = Depends(get_current_admin),
        db: Session = Depends(get_db)
):
    reservation_time_slot_service = ReservationTimeSlotService(db)
    updated_time_slot = reservation_time_slot_service.update_reservation_time_slot(venue_id, time_slot_id, time_slot)
    if not updated_time_slot:
        raise HTTPException(status_code=404, detail="Reservation time slot not found")
    return updated_time_slot


@router.delete("/venues/{venue_id}/reservation-time-slots/{time_slot_id}")
def delete_reservation_time_slot(
        venue_id: int,
        time_slot_id: int,
        current_user: User = Depends(get_current_admin),
        db: Session = Depends(get_db)
):
    reservation_time_slot_service = ReservationTimeSlotService(db)
    deleted_time_slot = reservation_time_slot_service.delete_reservation_time_slot(venue_id, time_slot_id)
    if not deleted_time_slot:
        raise HTTPException(status_code=404, detail="Reservation time slot not found")
    return {"message": "Reservation time slot deleted successfully"}
