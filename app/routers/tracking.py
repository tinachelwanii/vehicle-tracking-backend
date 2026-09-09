
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.database import get_db
from app.dependencies.auth import get_current_user
from app.models.user import User
from app.models.route import Route
from app.models.vehicle import Vehicle
from app.models.gps_data import GPSData


router = APIRouter(
    prefix="/api/me",
    tags=["My Tracking"]
)


# --------------------------------------------------
# GET ASSIGNED ROUTE
# --------------------------------------------------

@router.get("/route")
def get_my_route(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    route = (
        db.query(Route)
        .filter(Route.id == current_user.route_id)
        .first()
    )

    if not route:
        raise HTTPException(
            status_code=404,
            detail="Assigned route not found"
        )

    return {
        "route_id": route.id,
        "route_name": route.name,
        "description": route.description,
        "start_location": route.start_location,
        "end_location": route.end_location,
        "route_coordinates": route.route_coordinates
    }


# --------------------------------------------------
# GET ASSIGNED VEHICLE
# --------------------------------------------------

@router.get("/vehicle")
def get_my_vehicle(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    vehicle = (
        db.query(Vehicle)
        .filter(Vehicle.id == current_user.vehicle_id)
        .first()
    )

    if not vehicle:
        raise HTTPException(
            status_code=404,
            detail="Assigned vehicle not found"
        )

    return {
        "vehicle_id": vehicle.id,
        "vehicle_number": vehicle.vehicle_number,
        "status": vehicle.status,
        "route_id": vehicle.route_id
    }


# --------------------------------------------------
# GET CURRENT / LATEST VEHICLE LOCATION
# --------------------------------------------------

@router.get("/vehicle/location")
def get_my_vehicle_location(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    latest_gps = (
        db.query(GPSData)
        .filter(
            GPSData.vehicle_id == current_user.vehicle_id
        )
        .order_by(
            GPSData.timestamp.desc()
        )
        .first()
    )

    if not latest_gps:
        return {
            "message": "No GPS data available for your vehicle"
        }

    return {
        "vehicle_id": latest_gps.vehicle_id,
        "latitude": latest_gps.latitude,
        "longitude": latest_gps.longitude,
        "speed": latest_gps.speed,
        "timestamp": latest_gps.timestamp
    }
# --------------------------------------------------
# GET HISTORICAL GPS DATA
# --------------------------------------------------

@router.get("/vehicle/history")
def get_my_vehicle_history(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    history = (
        db.query(GPSData)
        .filter(
            GPSData.vehicle_id == current_user.vehicle_id
        )
        .order_by(
            GPSData.timestamp.asc()
        )
        .all()
    )

    return [
        {
            "vehicle_id": gps.vehicle_id,
            "latitude": gps.latitude,
            "longitude": gps.longitude,
            "speed": gps.speed,
            "timestamp": gps.timestamp
        }
        for gps in history
    ]