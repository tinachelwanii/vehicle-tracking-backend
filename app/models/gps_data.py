from sqlalchemy import Column, Integer, Float, DateTime, ForeignKey
from sqlalchemy.orm import relationship

from app.database import Base


class GPSData(Base):
    __tablename__ = "gps_data"

    id = Column(Integer, primary_key=True, index=True)

    vehicle_id = Column(
        Integer,
        ForeignKey("vehicles.id"),
        nullable=False,
        index=True
    )

    latitude = Column(
        Float,
        nullable=False
    )

    longitude = Column(
        Float,
        nullable=False
    )

    speed = Column(
        Float,
        default=0
    )

    timestamp = Column(
        DateTime,
        nullable=False
    )

    vehicle = relationship("Vehicle")