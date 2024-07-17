from sqlalchemy import Column, Integer, String, Boolean, TIMESTAMP, text, Enum as SqlAlchemyEnum
from sqlalchemy.orm import relationship
from app.db.database import Base
from enum import Enum


class UserRole(Enum):
    EMPLOYEE = "employee"
    VIP = "vip"
    ADMIN = "admin"


class User(Base):
    __tablename__ = "user"

    id = Column(Integer, primary_key=True, autoincrement=True)
    username = Column(String(50), unique=True, nullable=False)
    password = Column(String(100), nullable=False)
    email = Column(String(100), unique=True, nullable=False)
    phone = Column(String(20), nullable=False)
    role = Column(SqlAlchemyEnum(UserRole), nullable=False, default=UserRole.EMPLOYEE)
    is_leader = Column(Boolean, nullable=False, default=False)
    full_name = Column(String(50))
    department = Column(String(50))
    preferred_sports = Column(String(100))
    preferred_time = Column(String(100))
    created_at = Column(TIMESTAMP, nullable=False, server_default=text("CURRENT_TIMESTAMP"))
    updated_at = Column(TIMESTAMP, nullable=False, server_default=text("CURRENT_TIMESTAMP"), onupdate=text("CURRENT_TIMESTAMP"))

    reservations = relationship("Reservation", back_populates="user")
    feedbacks = relationship("Feedback", back_populates="user")
    notifications = relationship("Notification", back_populates="user")
    leader_reserved_times = relationship("LeaderReservedTime", back_populates="user")
    waiting_lists = relationship("WaitingList", back_populates="user")
    recurring_reservations = relationship("RecurringReservation", back_populates="user")

    @property
    def is_admin(self):
        return self.role == UserRole.ADMIN

    @classmethod
    def admin_role(cls):
        return UserRole.ADMIN
