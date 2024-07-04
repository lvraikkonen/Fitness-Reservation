from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.deps import get_db, get_current_user, get_current_admin
from app.models.user import User
from app.models.facility import Facility
from app.schemas.facility import FacilityCreate, FacilityUpdate
from app.services.facility_service import FacilityService

router = APIRouter()


@router.get("/venues/{venue_id}/facilities")
def get_venue_facilities(venue_id: int, db: Session = Depends(get_db)):
    facility_service = FacilityService(db)
    facilities = facility_service.get_facilities(venue_id)
    return facilities


@router.get("/facilities/{facility_id}")
def get_facility(facility_id: int, db: Session = Depends(get_db)):
    facility_service = FacilityService(db)
    facility = facility_service.get_facility(facility_id)
    if not facility:
        raise HTTPException(status_code=404, detail="Facility not found")
    return facility


@router.post("/venues/{venue_id}/facilities")
def create_facility(
        venue_id: int,
        facility: FacilityCreate,
        current_user: User = Depends(get_current_admin),
        db: Session = Depends(get_db)
):
    facility_service = FacilityService(db)
    created_facility = facility_service.create_facility(venue_id, facility)
    return created_facility


@router.put("/facilities/{facility_id}")
def update_facility(
        facility_id: int,
        facility: FacilityUpdate,
        current_user: User = Depends(get_current_admin),
        db: Session = Depends(get_db)
):
    facility_service = FacilityService(db)
    updated_facility = facility_service.update_facility(facility_id, facility)
    if not updated_facility:
        raise HTTPException(status_code=404, detail="Facility not found")
    return updated_facility


@router.delete("/facilities/{facility_id}")
def delete_facility(
        facility_id: int,
        current_user: User = Depends(get_current_admin),
        db: Session = Depends(get_db)
):
    facility_service = FacilityService(db)
    deleted_facility = facility_service.delete_facility(facility_id)
    if not deleted_facility:
        raise HTTPException(status_code=404, detail="Facility not found")
    return {"message": "Facility deleted successfully"}
