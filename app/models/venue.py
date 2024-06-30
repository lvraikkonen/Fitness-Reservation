from sqlalchemy import Column, Integer, String, Text, Enum, ForeignKey
from sqlalchemy.orm import relationship
from app.db.database import Base


class VenueStatus(str, Enum):
    OPEN = "open"
    CLOSED = "closed"
    MAINTENANCE = "maintenance"


class Venue(Base):
    __tablename__ = "venues"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), unique=True, index=True)
    location = Column(String(100))
    description = Column(Text)
    status = Column(Enum(VenueStatus), default=VenueStatus.OPEN)
    max_capacity = Column(Integer)
    open_time = Column(String(10))
    close_time = Column(String(10))

    images = relationship("VenueImage", back_populates="venue")


class VenueImage(Base):
    __tablename__ = "venue_images"

    id = Column(Integer, primary_key=True, index=True)
    venue_id = Column(Integer, ForeignKey("venues.id"))
    image_url = Column(String(200))

    venue = relationship("Venue", back_populates="images")
