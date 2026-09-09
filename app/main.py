
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy import text

from app.database import engine, Base
from app.models import Route, Vehicle, User, GPSData

from app.routers.auth import router as auth_router
from app.routers.tracking import router as tracking_router

from app.services.mqtt_service import start_mqtt


# ============================================================
# CREATE DATABASE TABLES
# ============================================================

Base.metadata.create_all(bind=engine)


# ============================================================
# CREATE FASTAPI APPLICATION
# ============================================================

app = FastAPI(
    title="Vehicle Tracking API",
    description="GPS based vehicle tracking system",
    version="1.0.0"
)


# ============================================================
# CORS CONFIGURATION
# ============================================================
# Required because Flutter Web runs in Chrome on a different
# origin/port than the FastAPI backend.

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
)


# ============================================================
# START MQTT SERVICE
# ============================================================

mqtt_client = start_mqtt()


# ============================================================
# REGISTER API ROUTERS
# ============================================================

app.include_router(auth_router)
app.include_router(tracking_router)


# ============================================================
# ROOT ENDPOINT
# ============================================================

@app.get("/")
def root():
    return {
        "message": "Vehicle Tracking API is running"
    }


# ============================================================
# HEALTH CHECK
# ============================================================

@app.get("/health")
def health():
    return {
        "status": "healthy"
    }


# ============================================================
# DATABASE CONNECTION TEST
# ============================================================

@app.get("/db-test")
def database_test():
    try:
        with engine.connect() as connection:
            connection.execute(text("SELECT 1"))

        return {
            "database": "connected"
        }

    except Exception as e:
        return {
            "database": "connection failed",
            "error": str(e)
        }

