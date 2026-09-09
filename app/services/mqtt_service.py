import json
from datetime import datetime

import paho.mqtt.client as mqtt
from sqlalchemy.orm import Session

from app.database import SessionLocal
from app.models.gps_data import GPSData
from app.models.vehicle import Vehicle


MQTT_HOST = "localhost"
MQTT_PORT = 1883
MQTT_TOPIC = "vehicles/+/gps"


def on_connect(client, userdata, flags, reason_code, properties):
    print("Connected to MQTT broker")

    client.subscribe(MQTT_TOPIC)

    print(f"Subscribed to: {MQTT_TOPIC}")


def on_message(client, userdata, msg):
    try:
        print(f"MQTT message received: {msg.topic}")

        data = json.loads(msg.payload.decode())

        vehicle_id = data["vehicle_id"]
        latitude = data["latitude"]
        longitude = data["longitude"]
        speed = data.get("speed", 0)

        timestamp_string = data.get("timestamp")

        if timestamp_string:
            timestamp = datetime.fromisoformat(
                timestamp_string.replace("Z", "+00:00")
            )
        else:
            timestamp = datetime.utcnow()

        db: Session = SessionLocal()

        try:
            vehicle = (
                db.query(Vehicle)
                .filter(Vehicle.id == vehicle_id)
                .first()
            )

            if not vehicle:
                print(
                    f"Vehicle {vehicle_id} does not exist"
                )
                return

            gps_record = GPSData(
                vehicle_id=vehicle_id,
                latitude=latitude,
                longitude=longitude,
                speed=speed,
                timestamp=timestamp
            )

            db.add(gps_record)

            vehicle.status = "ONLINE"

            db.commit()

            print(
                f"GPS saved: vehicle={vehicle_id}, "
                f"lat={latitude}, "
                f"lon={longitude}, "
                f"speed={speed}"
            )

        except Exception as e:
            db.rollback()
            print("Database error:", e)

        finally:
            db.close()

    except Exception as e:
        print("MQTT message error:", e)


def start_mqtt():

    client = mqtt.Client(
        mqtt.CallbackAPIVersion.VERSION2
    )

    client.on_connect = on_connect
    client.on_message = on_message

    print("Connecting to MQTT broker...")

    client.connect(
        MQTT_HOST,
        MQTT_PORT,
        60
    )

    client.loop_start()

    return client