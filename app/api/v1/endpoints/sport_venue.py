from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.deps import get_db, get_current_user, get_current_admin

from app.models.user import User
from app.models.sport_venue import SportVenue
from app.schemas.sport_venue import SportVenueCreate, SportVenueUpdate
from app.services.sport_venue_service import SportVenueService

router = APIRouter()


@router.get("/sport-venues")
def get_sport_venues(db: Session = Depends(get_db)):
    sport_venue_service = SportVenueService(db)
    sport_venues = sport_venue_service.get_sport_venues()
    return sport_venues


@router.post("/sport-venues")
def create_sport_venue(sport_venue: SportVenueCreate, current_user: User = Depends(get_current_admin), db: Session = Depends(get_db)):
    sport_venue_service = SportVenueService(db)
    created_sport_venue = sport_venue_service.create_sport_venue(sport_venue)
    return created_sport_venue


@router.get("/sport-venues/{sport_venue_id}")
def get_sport_venue(sport_venue_id: int, db: Session = Depends(get_db)):
    sport_venue_service = SportVenueService(db)
    sport_venue = sport_venue_service.get_sport_venue(sport_venue_id)
    if not sport_venue:
        raise HTTPException(status_code=404, detail="Sport venue not found")
    return sport_venue


@router.put("/sport-venues/{sport_venue_id}")
def update_sport_venue(sport_venue_id: int, sport_venue: SportVenueUpdate, current_user: User = Depends(get_current_admin), db: Session = Depends(get_db)):
    sport_venue_service = SportVenueService(db)
    updated_sport_venue = sport_venue_service.update_sport_venue(sport_venue_id, sport_venue)
    if not updated_sport_venue:
        raise HTTPException(status_code=404, detail="Sport venue not found")
    return updated_sport_venue


@router.delete("/sport-venues/{sport_venue_id}")
def delete_sport_venue(sport_venue_id: int, current_user: User = Depends(get_current_admin), db: Session = Depends(get_db)):
    sport_venue_service = SportVenueService(db)
    deleted_sport_venue = sport_venue_service.delete_sport_venue(sport_venue_id)
    if not deleted_sport_venue:
        raise HTTPException(status_code=404, detail="Sport venue not found")
    return {"message": "Sport venue deleted successfully"}
