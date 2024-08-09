from sqlalchemy import Column, Integer, String, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from app.db.database import Base


class UserActivity(Base):
    __tablename__ = "user_activity"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("user.id"), nullable=False)
    activity_type = Column(String, nullable=False)
    reservation_id = Column(Integer, ForeignKey("reservation.id"), nullable=True)
    venue_id = Column(Integer, ForeignKey("venue.id"), nullable=True)
    timestamp = Column(DateTime, nullable=False)
    details = Column(String, nullable=True)

    user = relationship("User", back_populates="activities")
    reservation = relationship("Reservation", back_populates="activities")
    venue = relationship("Venue", back_populates="activities")
