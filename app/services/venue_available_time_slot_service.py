from sqlalchemy import and_
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError
from app.models.venue import Venue
from app.models.venue_available_time_slot import VenueAvailableTimeSlot
from app.schemas.venue_available_time_slot import VenueAvailableTimeSlotCreate, VenueAvailableTimeSlotUpdate
from app.services.venue_service import VenueService
from typing import List, Optional
from datetime import date, datetime, timedelta, time
from app.core.config import get_logger

logger = get_logger(__name__)


class VenueAvailableTimeSlotService:
    def __init__(self, db: Session):
        self.db = db
        self.venue_service = VenueService(db)

    def create_time_slot(self, time_slot: VenueAvailableTimeSlotCreate) -> VenueAvailableTimeSlot:
        venue = self.venue_service.get_venue(time_slot.venue_id)
        if not venue:
            raise ValueError("Venue not found")

        if time_slot.capacity > venue.capacity:
            raise ValueError(f"Time slot capacity cannot exceed venue capacity of {venue.capacity}")

        db_time_slot = VenueAvailableTimeSlot(**time_slot.model_dump())
        self.db.add(db_time_slot)
        try:
            self.db.commit()
            self.db.refresh(db_time_slot)
        except IntegrityError:
            self.db.rollback()
            raise ValueError("Time slot already exists for this venue at the specified date and time")
        return db_time_slot

    def get_time_slot(self, time_slot_id: int) -> Optional[VenueAvailableTimeSlot]:
        return self.db.query(VenueAvailableTimeSlot).filter(VenueAvailableTimeSlot.id == time_slot_id).first()

    def get_time_slots_by_venue(self, venue_id: int, start_date: date, end_date: date) -> List[VenueAvailableTimeSlot]:
        return self.db.query(VenueAvailableTimeSlot).filter(
            VenueAvailableTimeSlot.venue_id == venue_id,
            VenueAvailableTimeSlot.date >= start_date,
            VenueAvailableTimeSlot.date <= end_date
        ).all()

    def update_time_slot(self, venue_id: int, slot_id: int, slot_update: VenueAvailableTimeSlotUpdate) -> Optional[
        VenueAvailableTimeSlot]:
        db_time_slot = self.get_time_slot(slot_id)
        if not db_time_slot or db_time_slot.venue_id != venue_id:
            return None

        update_data = slot_update.model_dump(exclude_unset=True)

        if 'capacity' in update_data:
            venue = self.venue_service.get_venue(venue_id)
            if update_data['capacity'] > venue.capacity:
                raise ValueError(f"Time slot capacity cannot exceed venue capacity of {venue.capacity}")

        for key, value in update_data.items():
            setattr(db_time_slot, key, value)

        try:
            self.db.commit()
            self.db.refresh(db_time_slot)
        except IntegrityError:
            self.db.rollback()
            raise ValueError("Update would result in a duplicate time slot")

        return db_time_slot

    def delete_time_slot(self, time_slot_id: int) -> bool:
        db_time_slot = self.get_time_slot(time_slot_id)
        if not db_time_slot:
            return False

        self.db.delete(db_time_slot)
        self.db.commit()
        return True

    def get_available_slots(self, venue_id: int, start_date: date, end_date: date) -> List[VenueAvailableTimeSlot]:
        return self.db.query(VenueAvailableTimeSlot).filter(
            VenueAvailableTimeSlot.venue_id == venue_id,
            VenueAvailableTimeSlot.date >= start_date,
            VenueAvailableTimeSlot.date <= end_date,
            VenueAvailableTimeSlot.capacity > 0
        ).all()

    def create_future_time_slot(self, days_ahead: int = 14):
        """
        为所有场馆创建未来指定天数的可用时间段
        """
        today = datetime.now().date()
        end_date = today + timedelta(days=days_ahead)

        # 获取所有场馆
        venues = self.db.query(Venue).all()

        for venue in venues:
            # 获取该场馆已存在的未来时间段
            existing_slots = self.db.query(VenueAvailableTimeSlot).filter(
                and_(
                    VenueAvailableTimeSlot.venue_id == venue.id,
                    VenueAvailableTimeSlot.date >= today,
                    VenueAvailableTimeSlot.date <= end_date
                )
            ).all()

            existing_slots_set = {(slot.date, slot.start_time, slot.end_time) for slot in existing_slots}

            # 为每一天创建时间段
            for day in range(days_ahead + 1):
                current_date = today + timedelta(days=day)

                # 这里假设每个场馆每天的开放时间是 9:00 到 22:00，每个时间段为 1 小时
                # 您可以根据实际需求调整这个逻辑
                for hour in range(9, 22):
                    start_time = time(hour, 0)
                    end_time = time(hour + 1, 0)

                    # 检查该时间段是否已存在
                    if (current_date, start_time, end_time) not in existing_slots_set:
                        new_slot = VenueAvailableTimeSlot(
                            venue_id=venue.id,
                            date=current_date,
                            start_time=start_time,
                            end_time=end_time,
                            capacity=venue.default_capacity  # 使用场馆的默认容量
                        )
                        self.db.add(new_slot)

        self.db.commit()
        logger.info(f"Created future time slots for the next {days_ahead} days for all venues.")
