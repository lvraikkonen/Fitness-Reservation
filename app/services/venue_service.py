from sqlalchemy.orm import Session
from app.models.venue import Venue, VenueImage
from app.schemas.venue import VenueCreate, VenueUpdate, VenueImageCreate


def get_venues(db: Session, skip: int = 0, limit: int = 100):
    return db.query(Venue).offset(skip).limit(limit).all()


def get_venue(db: Session, venue_id: int):
    return db.query(Venue).filter(Venue.id == venue_id).first()


def create_venue(db: Session, venue: VenueCreate):
    db_venue = Venue(**venue.dict())
    db.add(db_venue)
    db.commit()
    db.refresh(db_venue)
    return db_venue


def update_venue(db: Session, venue_id: int, venue: VenueUpdate):
    db_venue = get_venue(db, venue_id)
    if db_venue:
        update_data = venue.dict(exclude_unset=True)
        for key, value in update_data.items():
            setattr(db_venue, key, value)
        db.commit()
        db.refresh(db_venue)
    return db_venue


def delete_venue(db: Session, venue_id: int):
    db_venue = get_venue(db, venue_id)
    if db_venue:
        db.delete(db_venue)
        db.commit()
    return db_venue


def create_venue_image(db: Session, venue_id: int, image: VenueImageCreate):
    db_image = VenueImage(**image.dict(), venue_id=venue_id)
    db.add(db_image)
    db.commit()
    db.refresh(db_image)
    return db_image
