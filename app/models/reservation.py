from sqlalchemy import Column, Integer, Boolean, ForeignKey, TIMESTAMP, text, Enum as SqlAlchemyEnum, Date, Time, String
from sqlalchemy.orm import relationship
from app.db.database import Base
from enum import Enum


class ReservationStatus(Enum):
    PENDING = "pending"
    CONFIRMED = "confirmed"
    CANCELLED = "cancelled"
    CHECKED_IN = "checked_in"


class Reservation(Base):
    __tablename__ = "reservation"

    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey("user.id"), nullable=False)
    venue_id = Column(Integer, ForeignKey("venue.id"), nullable=False)
    venue_available_time_slot_id = Column(Integer, ForeignKey("venue_available_time_slot.id"), nullable=False)
    status = Column(SqlAlchemyEnum(ReservationStatus), default=ReservationStatus.PENDING, nullable=False)
    date = Column(Date, nullable=False)  # 用户实际预约日期
    actual_start_time = Column(Time, nullable=False)  # 用户实际预约时间段
    actual_end_time = Column(Time, nullable=False)  # 用户实际预约时间段
    is_recurring = Column(Boolean, nullable=False, default=False)
    recurring_reservation_id = Column(Integer, ForeignKey("recurring_reservation.id"), nullable=True)
    created_at = Column(TIMESTAMP, nullable=False, server_default=text("CURRENT_TIMESTAMP"))
    updated_at = Column(TIMESTAMP, nullable=False, server_default=text("CURRENT_TIMESTAMP"),
                        onupdate=text("CURRENT_TIMESTAMP"))
    cancelled_at = Column(TIMESTAMP, nullable=True)
    checked_in_at = Column(TIMESTAMP, nullable=True)

    user = relationship("User", back_populates="reservations")
    venue = relationship("Venue", back_populates="reservations")
    venue_available_time_slot = relationship("VenueAvailableTimeSlot", back_populates="reservations")
    recurring_reservation = relationship("RecurringReservation", back_populates="reservations")
