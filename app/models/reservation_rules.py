from sqlalchemy import Column, Integer, ForeignKey, TIMESTAMP, text, Interval, Enum as SqlAlchemyEnum
from sqlalchemy.orm import relationship
from app.db.database import Base
from app.models.user import UserRole


class ReservationRules(Base):
    __tablename__ = "reservation_rules"

    id = Column(Integer, primary_key=True, autoincrement=True)
    venue_id = Column(Integer, ForeignKey("venue.id"), nullable=False)
    user_role = Column(SqlAlchemyEnum(UserRole), nullable=False, default=UserRole.EMPLOYEE)
    min_duration = Column(Interval, nullable=False)
    max_duration = Column(Interval, nullable=False)
    max_daily_reservations = Column(Integer, nullable=False)
    max_weekly_reservations = Column(Integer, nullable=False)
    max_monthly_reservations = Column(Integer, nullable=False)
    created_at = Column(TIMESTAMP, nullable=False, server_default=text("CURRENT_TIMESTAMP"))
    updated_at = Column(TIMESTAMP, nullable=False, server_default=text("CURRENT_TIMESTAMP"), onupdate=text("CURRENT_TIMESTAMP"))

    venue = relationship("Venue", back_populates="reservation_rules")
