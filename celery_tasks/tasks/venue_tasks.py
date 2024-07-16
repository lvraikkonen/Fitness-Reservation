from celery import shared_task
from app.db.database import SessionLocal
from app.services.venue_available_time_slot_service import VenueAvailableTimeSlotService


@shared_task
def create_future_venue_time_slot():
    db = SessionLocal()
    try:
        service = VenueAvailableTimeSlotService(db)
        service.create_future_time_slot()
    finally:
        db.close()
