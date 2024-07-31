from sqlalchemy import Column, Integer, ForeignKey, TIMESTAMP, text, Boolean
from sqlalchemy.orm import relationship
from app.db.database import Base


class WaitingList(Base):
    __tablename__ = "waiting_list"

    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey("user.id"), nullable=False)
    venue_available_time_slot_id = Column(Integer, ForeignKey("venue_available_time_slot.id"), nullable=False)  # 等待列表项通常与可用时间段关联，而不是与特定的预约关联
    is_expired = Column(Boolean, nullable=False, default=False)
    created_at = Column(TIMESTAMP, nullable=False, server_default=text("CURRENT_TIMESTAMP"))
    updated_at = Column(TIMESTAMP, nullable=False, server_default=text("CURRENT_TIMESTAMP"),
                        onupdate=text("CURRENT_TIMESTAMP"))

    user = relationship("User", back_populates="waiting_lists")
    venue_available_time_slot = relationship("VenueAvailableTimeSlot", back_populates="waiting_lists")
