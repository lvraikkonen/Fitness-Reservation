from sqlalchemy import Column, Integer, String, Text, ForeignKey, TIMESTAMP, text, Enum as SqlAlchemyEnum
from sqlalchemy.orm import relationship
from app.db.database import Base
from enum import Enum


class VenueStatus(Enum):
    OPEN = "open"
    CLOSED = "closed"
    MAINTENANCE = "maintenance"


class Venue(Base):
    __tablename__ = "venue"

    id = Column(Integer, primary_key=True, autoincrement=True)
    sport_venue_id = Column(Integer, ForeignKey("sport_venue.id"), nullable=False)
    name = Column(String(50), nullable=False)
    capacity = Column(Integer, nullable=False)
    status = Column(SqlAlchemyEnum(VenueStatus), default=VenueStatus.OPEN, nullable=False)
    notice = Column(Text)
    created_at = Column(TIMESTAMP, nullable=False, server_default=text("CURRENT_TIMESTAMP"))
    updated_at = Column(TIMESTAMP, nullable=False, server_default=text("CURRENT_TIMESTAMP"), onupdate=text("CURRENT_TIMESTAMP"))

    sport_venue = relationship("SportVenue", back_populates="venues")
    facilities = relationship("Facility", back_populates="venue")
    reservation_time_slots = relationship("ReservationTimeSlot", back_populates="venue")
    leader_reserved_times = relationship("LeaderReservedTime", back_populates="venue")
    feedbacks = relationship("Feedback", back_populates="venue")
