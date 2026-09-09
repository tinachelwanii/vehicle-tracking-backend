import json
import random
import time
from datetime import datetime, timezone

import paho.mqtt.client as mqtt


MQTT_HOST = "localhost"
MQTT_PORT = 1883


vehicles = [
    {
        "id": 1,
        "number": "BUS-001",
        "latitude": 22.7196,
        "longitude": 75.8577,
    },
    {
        "id": 2,
        "number": "BUS-002",
        "latitude": 23.2599,
        "longitude": 77.4126,
    },
]


client = mqtt.Client(
    mqtt.CallbackAPIVersion.VERSION2
)


print("Connecting to MQTT broker...")

client.connect(
    MQTT_HOST,
    MQTT_PORT,
    60
)

client.loop_start()

print("GPS Simulator started")
print("Publishing GPS for:")
print("BUS-001 -> Route A")
print("BUS-002 -> Route B")
print()


try:

    while True:

        for vehicle in vehicles:

            # Simulate vehicle movement
            vehicle["latitude"] += random.uniform(0.0001, 0.0005)
            vehicle["longitude"] += random.uniform(0.0001, 0.0005)

            speed = random.uniform(20, 50)

            topic = f"vehicles/{vehicle['id']}/gps"

            gps_data = {
                "vehicle_id": vehicle["id"],
                "latitude": round(vehicle["latitude"], 6),
                "longitude": round(vehicle["longitude"], 6),
                "speed": round(speed, 2),
                "timestamp": datetime.now(timezone.utc).isoformat(),
            }

            payload = json.dumps(gps_data)

            result = client.publish(
                topic,
                payload
            )

            print(
                f"{vehicle['number']} | "
                f"lat={gps_data['latitude']} | "
                f"lon={gps_data['longitude']} | "
                f"speed={gps_data['speed']} km/h"
            )

        print("-" * 60)

        time.sleep(5)


except KeyboardInterrupt:

    print("\nGPS Simulator stopped.")

finally:

    client.loop_stop()
    client.disconnect()