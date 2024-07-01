from sqlalchemy import Column, Integer, SmallInteger, Time, ForeignKey, TIMESTAMP, text
from sqlalchemy.orm import relationship
from app.db.database import Base


class LeaderReservedTime(Base):
    __tablename__ = "leader_reserved_time"

    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey("user.id"), nullable=False)
    venue_id = Column(Integer, ForeignKey("venue.id"), nullable=False)
    day_of_week = Column(SmallInteger, nullable=False)
    start_time = Column(Time, nullable=False)
    end_time = Column(Time, nullable=False)
    created_at = Column(TIMESTAMP, nullable=False, server_default=text("CURRENT_TIMESTAMP"))
    updated_at = Column(TIMESTAMP, nullable=False, server_default=text("CURRENT_TIMESTAMP"), onupdate=text("CURRENT_TIMESTAMP"))

    user = relationship("User", back_populates="leader_reserved_times")
    venue = relationship("Venue", back_populates="leader_reserved_times")
