from sqlalchemy import Column, Integer, String, ForeignKey
from sqlalchemy.orm import relationship

from app.database import Base


class Vehicle(Base):
    __tablename__ = "vehicles"

    id = Column(Integer, primary_key=True, index=True)

    vehicle_number = Column(
        String(50),
        unique=True,
        nullable=False
    )

    status = Column(
        String(30),
        default="OFFLINE"
    )

    route_id = Column(
        Integer,
        ForeignKey("routes.id"),
        nullable=False
    )

    route = relationship("Route")