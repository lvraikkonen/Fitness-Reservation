from sqlalchemy import Column, Integer, Date, Time, ForeignKey, TIMESTAMP, text
from sqlalchemy.orm import relationship
from app.db.database import Base


class ReservationTimeSlot(Base):
    __tablename__ = "reservation_time_slot"

    id = Column(Integer, primary_key=True, autoincrement=True)
    venue_id = Column(Integer, ForeignKey("venue.id"), nullable=False)
    date = Column(Date, nullable=False)
    start_time = Column(Time, nullable=False)
    end_time = Column(Time, nullable=False)
    created_at = Column(TIMESTAMP, nullable=False, server_default=text("CURRENT_TIMESTAMP"))
    updated_at = Column(TIMESTAMP, nullable=False, server_default=text("CURRENT_TIMESTAMP"), onupdate=text("CURRENT_TIMESTAMP"))

    venue = relationship("Venue", back_populates="reservation_time_slots")
    reservations = relationship("Reservation", back_populates="time_slot")
