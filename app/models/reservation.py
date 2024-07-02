from sqlalchemy import Column, Integer, String, ForeignKey, TIMESTAMP, text, Enum as SqlAlchemyEnum
from sqlalchemy.orm import relationship
from app.db.database import Base
from enum import Enum


class ReservationStatus(Enum):
    PENDING = "pending"
    CONFIRMED = "confirmed"
    CANCELLED = "cancelled"


class Reservation(Base):
    __tablename__ = "reservation"

    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey("user.id"), nullable=False)
    time_slot_id = Column(Integer, ForeignKey("reservation_time_slot.id"), nullable=False)
    status = Column(SqlAlchemyEnum(ReservationStatus), default=ReservationStatus.PENDING, nullable=False)
    created_at = Column(TIMESTAMP, nullable=False, server_default=text("CURRENT_TIMESTAMP"))
    updated_at = Column(TIMESTAMP, nullable=False, server_default=text("CURRENT_TIMESTAMP"), onupdate=text("CURRENT_TIMESTAMP"))

    user = relationship("User", back_populates="reservations")
    time_slot = relationship("ReservationTimeSlot", back_populates="reservations")
    waiting_lists = relationship("WaitingList", back_populates="reservation")
