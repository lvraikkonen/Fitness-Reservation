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
    sport_type = Column(String(50), nullable=False)
    capacity = Column(Integer, nullable=False)  # 表示场馆能够同时容纳的最大人数
    default_capacity = Column(Integer, nullable=False)  # 场馆在创建可预约时间段时的默认容量
    status = Column(SqlAlchemyEnum(VenueStatus), default=VenueStatus.OPEN, nullable=False)
    description = Column(Text)  # 场馆描述
    image_url = Column(String(255))  # 场馆图片 URL
    notice = Column(Text)
    created_at = Column(TIMESTAMP, nullable=False, server_default=text("CURRENT_TIMESTAMP"))
    updated_at = Column(TIMESTAMP, nullable=False, server_default=text("CURRENT_TIMESTAMP"), onupdate=text("CURRENT_TIMESTAMP"))

    sport_venue = relationship("SportVenue", back_populates="venues")
    facilities = relationship("Facility", back_populates="venue")
    reservations = relationship("Reservation", back_populates="venue")
    leader_reserved_times = relationship("LeaderReservedTime", back_populates="venue")
    feedbacks = relationship("Feedback", back_populates="venue")
    reservation_rules = relationship("ReservationRules", back_populates="venue")
    recurring_reservations = relationship("RecurringReservation", back_populates="venue")
    available_time_slots = relationship("VenueAvailableTimeSlot", back_populates="venue")
    activities = relationship("UserActivity", back_populates="venue")
