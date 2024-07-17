from sqlalchemy import Column, Integer, ForeignKey, TIMESTAMP, text, Boolean
from sqlalchemy.orm import relationship
from app.db.database import Base


class WaitingList(Base):
    __tablename__ = "waiting_list"

    id = Column(Integer, primary_key=True, autoincrement=True)
    reservation_id = Column(Integer, ForeignKey("reservation.id"), nullable=False)
    user_id = Column(Integer, ForeignKey("user.id"), nullable=False)
    is_expired = Column(Boolean, nullable=False, default=False)
    created_at = Column(TIMESTAMP, nullable=False, server_default=text("CURRENT_TIMESTAMP"))
    updated_at = Column(TIMESTAMP, nullable=False, server_default=text("CURRENT_TIMESTAMP"),
                        onupdate=text("CURRENT_TIMESTAMP"))

    reservation = relationship("Reservation", back_populates="waiting_lists")
    user = relationship("User", back_populates="waiting_lists")
