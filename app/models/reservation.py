from sqlalchemy import Column, Integer, ForeignKey, DateTime, Enum
from sqlalchemy.orm import relationship
from app.db.database import Base


class ReservationStatus(str, Enum):
    PENDING = "pending"
    CONFIRMED = "confirmed"
    CANCELLED = "cancelled"


class Reservation(Base):
    __tablename__ = "reservations"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    venue_id = Column(Integer, ForeignKey("venues.id"))
    start_time = Column(DateTime)
    end_time = Column(DateTime)
    status = Column(Enum(ReservationStatus), default=ReservationStatus.PENDING)

    user = relationship("User", back_populates="reservations")
    venue = relationship("Venue", back_populates="reservations")


class WaitingList(Base):
    __tablename__ = "waiting_lists"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    reservation_id = Column(Integer, ForeignKey("reservations.id"))

    user = relationship("User", back_populates="waiting_lists")
    reservation = relationship("Reservation", back_populates="waiting_lists")
