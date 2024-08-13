from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session
from typing import List, Optional
from app.deps import get_db, get_current_user, get_current_admin
from app.models.user import User
from app.models.venue import VenueStatus
from app.schemas.venue import VenueCreate, VenueUpdate, VenueRead, VenueStats
from app.services.venue_service import VenueService
from app.core.exceptions import VenueNotFoundError, VenueCreateError, VenueUpdateError, VenueDeleteError

router = APIRouter()


@router.get("/venues", response_model=List[VenueRead])
def list_venues(
    sport_venue_id: Optional[int] = None,
    sport_type: Optional[str] = None,
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=100),
    db: Session = Depends(get_db)
):
    venue_service = VenueService(db)
    return venue_service.get_venues(sport_venue_id=sport_venue_id, skip=skip, limit=limit)


@router.get("/venues/search", response_model=List[VenueRead])
def search_venues(
    query: Optional[str] = Query(None),
    sport_type: Optional[str] = None,
    limit: int = Query(10, ge=1, le=100),
    db: Session = Depends(get_db)
):
    venue_service = VenueService(db)
    return venue_service.search_venues(query, sport_type=sport_type, limit=limit)


@router.get("/venues/stats", response_model=VenueStats)
def get_venue_stats(
    db: Session = Depends(get_db)
):
    venue_service = VenueService(db)
    return venue_service.get_venue_stats()


@router.post("/venues", response_model=VenueRead, status_code=status.HTTP_201_CREATED)
def create_venue(
    venue: VenueCreate,
    current_user: User = Depends(get_current_admin),
    db: Session = Depends(get_db)
):
    try:
        venue_service = VenueService(db)
        return venue_service.create_venue(venue)
    except VenueCreateError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))


@router.get("/venues/{venue_id}", response_model=VenueRead)
def get_venue(venue_id: int, db: Session = Depends(get_db)):
    try:
        venue_service = VenueService(db)
        return venue_service.get_venue(venue_id)
    except VenueNotFoundError as e:
        raise HTTPException(status_code=e.status_code, detail=str(e))


@router.put("/venues/{venue_id}", response_model=VenueRead)
def update_venue(
    venue_id: int,
    venue: VenueUpdate,
    current_user: User = Depends(get_current_admin),
    db: Session = Depends(get_db)
):
    try:
        venue_service = VenueService(db)
        return venue_service.update_venue(venue_id, venue)
    except VenueNotFoundError as e:
        raise HTTPException(status_code=e.status_code, detail=str(e))
    except VenueUpdateError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))


@router.delete("/venues/{venue_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_venue(
    venue_id: int,
    current_user: User = Depends(get_current_admin),
    db: Session = Depends(get_db)
):
    try:
        venue_service = VenueService(db)
        venue_service.delete_venue(venue_id)
    except VenueNotFoundError as e:
        raise HTTPException(status_code=e.status_code, detail=str(e))
    except VenueDeleteError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))


@router.patch("/venues/{venue_id}/status", response_model=VenueRead)
def update_venue_status(
    venue_id: int,
    status: VenueStatus,
    current_user: User = Depends(get_current_admin),
    db: Session = Depends(get_db)
):
    try:
        venue_service = VenueService(db)
        return venue_service.update_venue_status(venue_id, status)
    except VenueNotFoundError as e:
        raise HTTPException(status_code=e.status_code, detail=str(e))
    except VenueUpdateError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))


@router.post("/venues/{venue_id}/maintenance", response_model=VenueRead)
def set_venue_maintenance(
    venue_id: int,
    current_user: User = Depends(get_current_admin),
    db: Session = Depends(get_db)
):
    try:
        venue_service = VenueService(db)
        return venue_service.set_venue_maintenance(venue_id)
    except VenueNotFoundError as e:
        raise HTTPException(status_code=e.status_code, detail=str(e))
    except VenueUpdateError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))


@router.post("/venues/batch", response_model=List[VenueRead])
def create_venues_batch(
    venues: List[VenueCreate],
    current_user: User = Depends(get_current_admin),
    db: Session = Depends(get_db)
):
    try:
        venue_service = VenueService(db)
        return venue_service.create_venues_batch(venues)
    except VenueCreateError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))


# @router.get("/{venue_id}/facilities", response_model=List[FacilityRead])
# def get_venue_facilities(venue_id: int, db: Session = Depends(get_db)):
#     venue_service = VenueService(db)
#     try:
#         return venue_service.get_venue_facilities(venue_id)
#     except VenueNotFoundError as e:
#         raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
