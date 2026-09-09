from sqlalchemy import Column, Integer, String, Text

from app.database import Base


class Route(Base):
    __tablename__ = "routes"

    id = Column(Integer, primary_key=True, index=True)

    name = Column(String(100), nullable=False)

    description = Column(Text, nullable=True)

    start_location = Column(String(255), nullable=False)

    end_location = Column(String(255), nullable=False)

    route_coordinates = Column(Text, nullable=True)