from datetime import datetime

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.gps_data import GPSData
from app.models.vehicle import Vehicle


router = APIRouter(
    prefix="/api/gps",
    tags=["GPS"]
)


# --------------------------------------------------
# GPS DATA REQUEST
# --------------------------------------------------

class GPSDataCreate(BaseModel):
    vehicle_id: int
    latitude: float
    longitude: float
    speed: float = 0
    timestamp: datetime


# --------------------------------------------------
# RECEIVE GPS DATA
# --------------------------------------------------

@router.post("/")
def receive_gps_data(
    gps_data: GPSDataCreate,
    db: Session = Depends(get_db)
):
    # Check that vehicle exists
    vehicle = (
        db.query(Vehicle)
        .filter(Vehicle.id == gps_data.vehicle_id)
        .first()
    )

    if not vehicle:
        raise HTTPException(
            status_code=404,
            detail="Vehicle not found"
        )

    # Create GPS record
    new_gps = GPSData(
        vehicle_id=gps_data.vehicle_id,
        latitude=gps_data.latitude,
        longitude=gps_data.longitude,
        speed=gps_data.speed,
        timestamp=gps_data.timestamp
    )

    db.add(new_gps)

    # Mark vehicle online when GPS data is received
    vehicle.status = "ONLINE"

    db.commit()
    db.refresh(new_gps)

    return {
        "message": "GPS data received successfully",
        "id": new_gps.id,
        "vehicle_id": new_gps.vehicle_id,
        "latitude": new_gps.latitude,
        "longitude": new_gps.longitude,
        "speed": new_gps.speed,
        "timestamp": new_gps.timestamp
    }