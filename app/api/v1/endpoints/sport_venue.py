from fastapi import APIRouter, Depends, status, Query
from sqlalchemy.orm import Session
from app.deps import get_db, get_current_user, get_current_admin
from typing import List, Optional

from app.models.user import User
from app.schemas.sport_venue import SportVenueCreate, SportVenueUpdate, SportVenueRead, SportVenueList
from app.schemas.venue import VenueRead
from app.services.sport_venue_service import SportVenueService
from app.core.exceptions import SportVenueDuplicateError
from app.core.config import get_logger

router = APIRouter()
logger = get_logger(__name__)


@router.get("/", response_model=SportVenueList, status_code=status.HTTP_200_OK)
def list_sport_venues(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=100),
    sort_by: str = Query("name", regex="^(name|location)$"),
    db: Session = Depends(get_db)
):
    sport_venue_service = SportVenueService(db)
    sport_venues = sport_venue_service.get_sport_venues(skip=skip, limit=limit, sort_by=sort_by)
    return {"items": sport_venues, "total": len(sport_venues)}


@router.post("/", response_model=SportVenueRead, status_code=status.HTTP_201_CREATED)
def create_sport_venue(
    sport_venue: SportVenueCreate,
    current_user: User = Depends(get_current_admin),
    db: Session = Depends(get_db)
):
    sport_venue_service = SportVenueService(db)
    return sport_venue_service.create_sport_venue(sport_venue)


@router.get("/search", response_model=List[SportVenueRead], status_code=status.HTTP_200_OK)
def search_sport_venues(
    query: str = Query(..., min_length=1, description="Search query string"),
    limit: int = Query(10, ge=1, le=100, description="Maximum number of results to return"),
    db: Session = Depends(get_db)
):
    sport_venue_service = SportVenueService(db)
    results = sport_venue_service.search_sport_venues(query, limit)
    logger.info(f"Found {len(results)} results for query: {query}")
    return results


@router.get("/{sport_venue_id}", response_model=SportVenueRead, status_code=status.HTTP_200_OK)
def get_sport_venue(sport_venue_id: int, db: Session = Depends(get_db)):
    sport_venue_service = SportVenueService(db)
    return sport_venue_service.get_sport_venue(sport_venue_id)


@router.put("/{sport_venue_id}", response_model=SportVenueRead, status_code=status.HTTP_200_OK)
def update_sport_venue(
    sport_venue_id: int,
    sport_venue: SportVenueUpdate,
    current_user: User = Depends(get_current_admin),
    db: Session = Depends(get_db)
):
    sport_venue_service = SportVenueService(db)
    return sport_venue_service.update_sport_venue(sport_venue_id, sport_venue)


@router.delete("/{sport_venue_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_sport_venue(
    sport_venue_id: int,
    current_user: User = Depends(get_current_admin),
    db: Session = Depends(get_db)
):
    sport_venue_service = SportVenueService(db)
    sport_venue_service.delete_sport_venue(sport_venue_id)
    return None


@router.get("/{sport_venue_id}/venues", response_model=List[VenueRead], status_code=status.HTTP_200_OK)
def list_venues_by_sport_venue(sport_venue_id: int, db: Session = Depends(get_db)):
    sport_venue_service = SportVenueService(db)
    return sport_venue_service.get_venues_by_sport_venue(sport_venue_id)
