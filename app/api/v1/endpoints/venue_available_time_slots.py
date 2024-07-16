from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import List
from datetime import date

from app.deps import get_db, get_current_admin
from app.models.user import User
from app.services.venue_available_time_slot_service import VenueAvailableTimeSlotService
from app.schemas.venue_available_time_slot import (
    VenueAvailableTimeSlotCreate,
    VenueAvailableTimeSlotUpdate,
    VenueAvailableTimeSlotInDB
)

router = APIRouter()


@router.get("/{venue_id}/available-slots", response_model=List[VenueAvailableTimeSlotInDB])
def get_available_slots(
    venue_id: int,
    start_date: date = Query(...),
    end_date: date = Query(...),
    db: Session = Depends(get_db)
):
    service = VenueAvailableTimeSlotService(db)
    slots = service.get_available_slots(venue_id, start_date, end_date)
    return slots


@router.post("/{venue_id}/available-slots", response_model=VenueAvailableTimeSlotInDB)
def create_available_slot(
    venue_id: int,
    slot: VenueAvailableTimeSlotCreate,
    current_user: User = Depends(get_current_admin),
    db: Session = Depends(get_db)
):
    service = VenueAvailableTimeSlotService(db)
    try:
        created_slot = service.create_time_slot(slot)
        return created_slot
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.put("/{venue_id}/available-slots/{slot_id}", response_model=VenueAvailableTimeSlotInDB)
def update_available_slot(
    venue_id: int,
    slot_id: int,
    slot_update: VenueAvailableTimeSlotUpdate,
    current_user: User = Depends(get_current_admin),
    db: Session = Depends(get_db)
):
    service = VenueAvailableTimeSlotService(db)
    try:
        updated_slot = service.update_time_slot(venue_id, slot_id, slot_update)
        if not updated_slot:
            raise HTTPException(status_code=404, detail="Time slot not found")
        return updated_slot
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.delete("/{venue_id}/available-slots/{slot_id}", response_model=bool)
def delete_available_slot(
    venue_id: int,
    slot_id: int,
    current_user: User = Depends(get_current_admin),
    db: Session = Depends(get_db)
):
    service = VenueAvailableTimeSlotService(db)
    deleted = service.delete_time_slot(slot_id)
    if not deleted:
        raise HTTPException(status_code=404, detail="Time slot not found")
    return True
