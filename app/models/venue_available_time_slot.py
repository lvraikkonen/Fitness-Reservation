from sqlalchemy import Column, Integer, Date, Time, ForeignKey, TIMESTAMP, text, UniqueConstraint
from sqlalchemy.orm import relationship
from app.db.database import Base


class VenueAvailableTimeSlot(Base):
    __tablename__ = "venue_available_time_slot"

    id = Column(Integer, primary_key=True, autoincrement=True)
    venue_id = Column(Integer, ForeignKey("venue.id"), nullable=False)
    date = Column(Date, nullable=False)
    start_time = Column(Time, nullable=False)
    end_time = Column(Time, nullable=False)
    capacity = Column(Integer, nullable=False)
    created_at = Column(TIMESTAMP, nullable=False, server_default=text("CURRENT_TIMESTAMP"))
    updated_at = Column(TIMESTAMP, nullable=False, server_default=text("CURRENT_TIMESTAMP"), onupdate=text("CURRENT_TIMESTAMP"))

    venue = relationship("Venue", back_populates="available_time_slots")

    __table_args__ = (
        UniqueConstraint('venue_id', 'date', 'start_time', 'end_time', name='uq_venue_date_time'),
    )
