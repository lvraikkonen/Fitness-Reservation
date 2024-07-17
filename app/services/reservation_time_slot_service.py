from sqlalchemy.orm import Session
from app.models.reservation_time_slot_delete import ReservationTimeSlot
from app.schemas.reservation_time_slot import ReservationTimeSlotCreate, ReservationTimeSlotUpdate


class ReservationTimeSlotService:
    def __init__(self, db: Session):
        self.db = db

    def create_reservation_time_slot(self, reservation_time_slot: ReservationTimeSlotCreate):
        db_reservation_time_slot = ReservationTimeSlot(**reservation_time_slot.dict())
        self.db.add(db_reservation_time_slot)
        self.db.commit()
        self.db.refresh(db_reservation_time_slot)
        return db_reservation_time_slot

    def get_reservation_time_slots(self, venue_id: int):
        return self.db.query(ReservationTimeSlot).filter(ReservationTimeSlot.venue_id == venue_id).all()

    def get_reservation_time_slot(self, reservation_time_slot_id: int):
        return self.db.query(ReservationTimeSlot).filter(ReservationTimeSlot.id == reservation_time_slot_id).first()

    def update_reservation_time_slot(self, reservation_time_slot_id: int, reservation_time_slot: ReservationTimeSlotUpdate):
        db_reservation_time_slot = self.db.query(ReservationTimeSlot).filter(ReservationTimeSlot.id == reservation_time_slot_id).first()
        if db_reservation_time_slot:
            update_data = reservation_time_slot.dict(exclude_unset=True)
            for key, value in update_data.items():
                setattr(db_reservation_time_slot, key, value)
            self.db.commit()
            self.db.refresh(db_reservation_time_slot)
        return db_reservation_time_slot

    def delete_reservation_time_slot(self, reservation_time_slot_id: int):
        db_reservation_time_slot = self.db.query(ReservationTimeSlot).filter(ReservationTimeSlot.id == reservation_time_slot_id).first()
        if db_reservation_time_slot:
            self.db.delete(db_reservation_time_slot)
            self.db.commit()
        return db_reservation_time_slot
