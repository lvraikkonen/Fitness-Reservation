from sqlalchemy import Column, Integer, String, ForeignKey
from sqlalchemy.orm import relationship
from app.db.database import Base


class Profile(Base):
    __tablename__ = "profiles"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), unique=True)
    full_name = Column(String(100))
    department = Column(String(100))
    contact_info = Column(String(100))
    preferred_sports = Column(String(100))
    preferred_time = Column(String(100))

    user = relationship("User", back_populates="profile")
