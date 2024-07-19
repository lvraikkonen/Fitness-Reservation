from sqlalchemy import and_
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError, SQLAlchemyError
from app.models.venue import Venue
from app.models.venue_available_time_slot import VenueAvailableTimeSlot
from app.schemas.venue_available_time_slot import VenueAvailableTimeSlotCreate, VenueAvailableTimeSlotUpdate
from app.services.venue_service import VenueService
from typing import List, Optional, Tuple, Union
from datetime import date, datetime, timedelta, time
from app.core.config import get_logger, settings
from app.core.exceptions import (
    VenueNotFoundError,
    TimeSlotExistsError,
    TimeSlotNotFoundError,
    CapacityExceededError,
    TimeSlotConflictError,
    ValidationError
)

logger = get_logger(__name__)


class VenueAvailableTimeSlotService:
    def __init__(self, db: Session):
        self.db = db
        self.venue_service = VenueService(db)
        self.settings = settings

    def create_time_slot(self, time_slot: VenueAvailableTimeSlotCreate) -> VenueAvailableTimeSlot:
        logger.info(f"Creating new time slot for venue {time_slot.venue_id}")
        venue = self.venue_service.get_venue(time_slot.venue_id)
        if not venue:
            raise VenueNotFoundError(f"Venue with id {time_slot.venue_id} not found")

        if time_slot.capacity > venue.capacity:
            raise CapacityExceededError(f"Time slot capacity cannot exceed venue capacity of {venue.capacity}")

        if time_slot.start_time >= time_slot.end_time:
            raise ValidationError("Start time must be before end time")

        if self._check_time_slot_conflict(time_slot):
            raise TimeSlotConflictError("Time slot conflicts with existing slots")

        db_time_slot = VenueAvailableTimeSlot(**time_slot.dict())
        self.db.add(db_time_slot)
        try:
            self.db.commit()
            self.db.refresh(db_time_slot)
            logger.info(f"Time slot created successfully: {db_time_slot.id}")
            return db_time_slot
        except IntegrityError:
            self.db.rollback()
            logger.error("Failed to create time slot due to integrity error")
            raise TimeSlotExistsError("Time slot already exists for this venue at the specified date and time")

    def get_time_slot(self, time_slot_id: int) -> Optional[VenueAvailableTimeSlot]:
        return self.db.query(VenueAvailableTimeSlot).filter(VenueAvailableTimeSlot.id == time_slot_id).first()

    def get_time_slots_by_venue(self, venue_id: int, start_date: date, end_date: date, page: int = 1,
                                page_size: int = 20) -> Tuple[List[VenueAvailableTimeSlot], int]:
        query = self.db.query(VenueAvailableTimeSlot).filter(
            VenueAvailableTimeSlot.venue_id == venue_id,
            VenueAvailableTimeSlot.date >= start_date,
            VenueAvailableTimeSlot.date <= end_date
        )
        total = query.count()
        time_slots = query.offset((page - 1) * page_size).limit(page_size).all()
        return time_slots, total

    def update_time_slot(self, venue_id: int, slot_id: int,
                         slot_update: VenueAvailableTimeSlotUpdate) -> VenueAvailableTimeSlot:
        logger.info(f"Updating time slot {slot_id} for venue {venue_id}")
        db_time_slot = self.get_time_slot(slot_id)
        if not db_time_slot or db_time_slot.venue_id != venue_id:
            raise TimeSlotNotFoundError(f"Time slot {slot_id} not found for venue {venue_id}")

        update_data = slot_update.dict(exclude_unset=True)

        if 'capacity' in update_data:
            venue = self.venue_service.get_venue(venue_id)
            if update_data['capacity'] > venue.capacity:
                raise CapacityExceededError(f"Time slot capacity cannot exceed venue capacity of {venue.capacity}")

        if 'start_time' in update_data and 'end_time' in update_data:
            if update_data['start_time'] >= update_data['end_time']:
                raise ValueError("Start time must be before end time")

        for key, value in update_data.items():
            setattr(db_time_slot, key, value)

        if self._check_time_slot_conflict(db_time_slot, exclude_id=slot_id):
            raise TimeSlotConflictError("Updated time slot conflicts with existing slots")

        try:
            self.db.commit()
            self.db.refresh(db_time_slot)
            logger.info(f"Time slot {slot_id} updated successfully")
            return db_time_slot
        except IntegrityError:
            self.db.rollback()
            logger.error(f"Failed to update time slot {slot_id} due to integrity error")
            raise TimeSlotExistsError("Update would result in a duplicate time slot")

    def delete_time_slot(self, time_slot_id: int) -> bool:
        logger.info(f"Deleting time slot {time_slot_id}")
        db_time_slot = self.get_time_slot(time_slot_id)
        if not db_time_slot:
            logger.warning(f"Attempted to delete non-existent time slot {time_slot_id}")
            return False

        # Here you might want to check for and handle any associated reservations
        # For example: cancel_associated_reservations(time_slot_id)

        self.db.delete(db_time_slot)
        self.db.commit()
        logger.info(f"Time slot {time_slot_id} deleted successfully")
        return True

    def get_available_slots(self, venue_id: int, start_date: date, end_date: date, page: int = 1,
                            page_size: int = 20) -> Tuple[List[VenueAvailableTimeSlot], int]:
        query = self.db.query(VenueAvailableTimeSlot).filter(
            VenueAvailableTimeSlot.venue_id == venue_id,
            VenueAvailableTimeSlot.date >= start_date,
            VenueAvailableTimeSlot.date <= end_date,
            VenueAvailableTimeSlot.capacity > 0
        )
        total = query.count()
        slots = query.offset((page - 1) * page_size).limit(page_size).all()
        return slots, total

    def create_future_time_slots(self, days_ahead: int = 14):
        logger.info(f"Creating future time slots for the next {days_ahead} days")
        today = datetime.now().date()
        end_date = today + timedelta(days=days_ahead)

        venues = self.db.query(Venue).all()

        try:
            for venue in venues:
                existing_slots = self.db.query(VenueAvailableTimeSlot).filter(
                    and_(
                        VenueAvailableTimeSlot.venue_id == venue.id,
                        VenueAvailableTimeSlot.date >= today,
                        VenueAvailableTimeSlot.date <= end_date
                    )
                ).all()

                existing_slots_set = {(slot.date, slot.start_time, slot.end_time) for slot in existing_slots}

                new_slots = []
                for day in range(days_ahead + 1):
                    current_date = today + timedelta(days=day)
                    for start_hour in range(self.settings.VENUE_OPEN_HOUR, self.settings.VENUE_CLOSE_HOUR):
                        start_time = time(start_hour, 0)
                        end_time = time(start_hour + 1, 0)

                        if (current_date, start_time, end_time) not in existing_slots_set:
                            new_slots.append(VenueAvailableTimeSlot(
                                venue_id=venue.id,
                                date=current_date,
                                start_time=start_time,
                                end_time=end_time,
                                capacity=venue.default_capacity
                            ))

                self.db.bulk_save_objects(new_slots)

            self.db.commit()
            logger.info(f"Successfully created future time slots for {len(venues)} venues")
        except SQLAlchemyError as e:
            self.db.rollback()
            logger.error(f"Failed to create future time slots: {str(e)}")
            raise

    def _check_time_slot_conflict(
            self,
            time_slot: Union[VenueAvailableTimeSlotCreate, VenueAvailableTimeSlot],
            exclude_id: Optional[int] = None
    ) -> bool:
        query = self.db.query(VenueAvailableTimeSlot).filter(
            VenueAvailableTimeSlot.venue_id == time_slot.venue_id,
            VenueAvailableTimeSlot.date == time_slot.date,
            VenueAvailableTimeSlot.start_time < time_slot.end_time,
            VenueAvailableTimeSlot.end_time > time_slot.start_time
        )

        if exclude_id:
            query = query.filter(VenueAvailableTimeSlot.id != exclude_id)

        return query.first() is not None
