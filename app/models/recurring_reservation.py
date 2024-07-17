from sqlalchemy import Column, Integer, ForeignKey, TIMESTAMP, text, Enum as SqlAlchemyEnum
from sqlalchemy.orm import relationship
from app.db.database import Base
from enum import Enum


class RecurrencePattern(Enum):
    DAILY = "daily"
    WEEKLY = "weekly"
    MONTHLY = "monthly"


class RecurringReservation(Base):
    __tablename__ = "recurring_reservation"

    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey("user.id"), nullable=False)
    venue_id = Column(Integer, ForeignKey("venue.id"), nullable=False)
    pattern = Column(SqlAlchemyEnum(RecurrencePattern), nullable=False)
    start_date = Column(TIMESTAMP, nullable=False)
    end_date = Column(TIMESTAMP, nullable=True)
    created_at = Column(TIMESTAMP, nullable=False, server_default=text("CURRENT_TIMESTAMP"))
    updated_at = Column(TIMESTAMP, nullable=False, server_default=text("CURRENT_TIMESTAMP"), onupdate=text("CURRENT_TIMESTAMP"))

    user = relationship("User", back_populates="recurring_reservations")
    venue = relationship("Venue", back_populates="recurring_reservations")
    reservations = relationship("Reservation", back_populates="recurring_reservation")
