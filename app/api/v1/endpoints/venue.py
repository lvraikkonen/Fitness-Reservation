from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
from app.api.deps import get_db
from app.schemas.venue import VenueCreate, VenueUpdate, VenueResponse, VenueImageCreate, VenueImageResponse
from app.services.venue_service import get_venues, get_venue, create_venue, update_venue, delete_venue, create_venue_image

router = APIRouter()


@router.get("/", response_model=List[VenueResponse])
def read_venues(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    venues = get_venues(db, skip=skip, limit=limit)
    return venues


@router.post("/", response_model=VenueResponse)
def create_venue_endpoint(venue: VenueCreate, db: Session = Depends(get_db)):
    return create_venue(db, venue)


@router.get("/{venue_id}", response_model=VenueResponse)
def read_venue(venue_id: int, db: Session = Depends(get_db)):
    db_venue = get_venue(db, venue_id=venue_id)
    if db_venue is None:
        raise HTTPException(status_code=404, detail="Venue not found")
    return db_venue


@router.patch("/{venue_id}", response_model=VenueResponse)
def update_venue_endpoint(venue_id: int, venue: VenueUpdate, db: Session = Depends(get_db)):
    db_venue = update_venue(db, venue_id=venue_id, venue=venue)
    if db_venue is None:
        raise HTTPException(status_code=404, detail="Venue not found")
    return db_venue


@router.delete("/{venue_id}", response_model=VenueResponse)
def delete_venue_endpoint(venue_id: int, db: Session = Depends(get_db)):
    db_venue = delete_venue(db, venue_id=venue_id)
    if db_venue is None:
        raise HTTPException(status_code=404, detail="Venue not found")
    return db_venue


@router.post("/{venue_id}/images", response_model=VenueImageResponse)
def create_venue_image_endpoint(venue_id: int, image: VenueImageCreate, db: Session = Depends(get_db)):
    return create_venue_image(db, venue_id=venue_id, image=image)
