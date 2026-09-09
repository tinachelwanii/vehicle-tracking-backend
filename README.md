# vehicle-tracking-backend
# Vehicle Tracking System — FastAPI Backend

A GPS-based vehicle tracking backend built with **Python FastAPI**, **PostgreSQL**, **SQLAlchemy**, **JWT authentication**, and **MQTT**.

The backend manages users, bus routes, vehicles, GPS tracking data, authentication, route/vehicle assignments, and real-time GPS data received through MQTT.

---

##  Technology Stack

* **Python 3.x**
* **FastAPI** — REST API framework
* **PostgreSQL** — Relational database
* **SQLAlchemy** — ORM
* **JWT** — Authentication
* **Paho MQTT** — MQTT client
* **Uvicorn** — ASGI server
* **python-dotenv** — Environment configuration
* **OAuth2 Password Flow** — Login authentication

---

## System Architecture

```text
                    ┌──────────────────────┐
                    │    Flutter App       │
                    │                      │
                    │ Login                │
                    │ Route                │
                    │ Vehicle              │
                    │ Live Map             │
                    │ GPS History          │
                    └──────────┬───────────┘
                               │
                         REST API / JWT
                               │
                               ▼
                    ┌──────────────────────┐
                    │    FastAPI Backend   │
                    │                      │
                    │ Authentication       │
                    │ Route APIs            │
                    │ Vehicle APIs          │
                    │ Location APIs         │
                    │ History APIs          │
                    └───────┬───────┬──────┘
                            │       │
                  SQLAlchemy│       │MQTT
                            │       │
                            ▼       ▼
                   ┌────────────┐  ┌──────────────┐
                   │ PostgreSQL │  │ MQTT Broker  │
                   │            │  │              │
                   │ Users      │  │ GPS messages │
                   │ Routes     │  └──────┬───────┘
                   │ Vehicles   │         │
                   │ GPS Data   │         │
                   └────────────┘         │
                                         ▲
                                         │
                              ┌──────────┴──────────┐
                              │   GPS Simulator     │
                              │                     │
                              │ BUS-001             │
                              │ BUS-002             │
                              └─────────────────────┘
```

---

##  Database Design

The application uses PostgreSQL.

### Users

Stores application users and their assigned route and vehicle.

| Column        | Type    | Description       |
| ------------- | ------- | ----------------- |
| id            | Integer | Primary key       |
| email         | String  | Unique user email |
| password_hash | String  | Hashed password   |
| route_id      | Integer | Assigned route    |
| vehicle_id    | Integer | Assigned vehicle  |

### Routes

Stores bus route information.

| Column            | Type    | Description       |
| ----------------- | ------- | ----------------- |
| id                | Integer | Primary key       |
| name              | String  | Route name        |
| description       | Text    | Route description |
| start_location    | String  | Starting location |
| end_location      | String  | Destination       |
| route_coordinates | Text    | Route coordinates |

### Vehicles

Stores vehicle information.

| Column         | Type    | Description        |
| -------------- | ------- | ------------------ |
| id             | Integer | Primary key        |
| vehicle_number | String  | Vehicle identifier |
| status         | String  | ONLINE/OFFLINE     |
| route_id       | Integer | Assigned route     |

### GPS Data

Stores current and historical GPS information.

| Column     | Type     | Description       |
| ---------- | -------- | ----------------- |
| id         | Integer  | Primary key       |
| vehicle_id | Integer  | Vehicle reference |
| latitude   | Float    | GPS latitude      |
| longitude  | Float    | GPS longitude     |
| speed      | Float    | Vehicle speed     |
| timestamp  | DateTime | GPS timestamp     |

### Relationships

```text
User
 ├── route_id ──────► Route
 └── vehicle_id ────► Vehicle
                         │
                         └── route_id ──────► Route

Vehicle
 └── vehicle_id ◄──── GPSData
```

---

## Authentication

Authentication is implemented using **JWT Bearer tokens**.

### Login Flow

```text
Flutter
   │
   │ email + password
   ▼
POST /api/auth/login
   │
   ▼
FastAPI authenticates user
   │
   ▼
JWT access token
   │
   ▼
Flutter stores token
   │
   ▼
Authorization: Bearer <token>
```

The token contains the authenticated user's ID.

Protected APIs use the authenticated user to determine which route and vehicle they are allowed to access.

---

##  Route and Vehicle Assignment

Each user is assigned:

* One bus route
* One vehicle

Example seed data:

```text
User A
Email: usera@example.com
Route: Route A
Vehicle: BUS-001

User B
Email: userb@example.com
Route: Route B
Vehicle: BUS-002
```

The backend does not allow a user to arbitrarily request another vehicle through the protected `/api/me` APIs.

For example:

```text
User A → vehicle_id = 1 → BUS-001
User B → vehicle_id = 2 → BUS-002
```

The authenticated user's `vehicle_id` is used when retrieving location and history.

---

## MQTT GPS Data Flow

MQTT is used to receive GPS data from vehicles.

MQTT topic pattern:

```text
vehicles/{vehicle_id}/gps
```

Examples:

```text
vehicles/1/gps
vehicles/2/gps
```

Example GPS payload:

```json
{
  "vehicle_id": 1,
  "latitude": 22.7196,
  "longitude": 75.8577,
  "speed": 35,
  "timestamp": "2026-09-09T12:00:00"
}
```

### GPS Processing Flow

```text
GPS Simulator / Vehicle
          │
          │ MQTT
          ▼
    MQTT Broker
          │
          ▼
 FastAPI MQTT Service
          │
          ├── Validate vehicle
          │
          ├── Read GPS data
          │
          ├── Store GPS record
          │
          └── Set vehicle ONLINE
                  │
                  ▼
              PostgreSQL
```

The backend maintains historical GPS records rather than replacing previous locations.

---

## GPS Simulator

A GPS simulator is included for testing.

Location:

```text
app/simulator/gps_simulator.py
```

The simulator publishes GPS data for multiple vehicles approximately every 5 seconds.

Current simulated vehicles include:

```text
BUS-001 → Vehicle ID 1
BUS-002 → Vehicle ID 2
```

Run the simulator with:

```powershell
python .\app\simulator\gps_simulator.py
```

Make sure an MQTT broker is running before starting the simulator.

---

## API Endpoints

### Authentication

#### Login

```http
POST /api/auth/login
```

Request:

```text
Content-Type: application/x-www-form-urlencoded
```

Parameters:

```text
username=usera@example.com
password=password123
```

Response:

```json
{
  "access_token": "<JWT_TOKEN>",
  "token_type": "bearer"
}
```

---

### Assigned Route

```http
GET /api/me/route
```

Requires:

```http
Authorization: Bearer <JWT_TOKEN>
```

Returns the authenticated user's assigned route.

Example:

```json
{
  "route_id": 1,
  "route_name": "Route A",
  "description": "...",
  "start_location": "Indore",
  "end_location": "Vijay Nagar",
  "route_coordinates": "22.7196,75.8577;22.7533,75.8937"
}
```

---

### Assigned Vehicle

```http
GET /api/me/vehicle
```

Returns the vehicle assigned to the authenticated user.

Example:

```json
{
  "vehicle_id": 1,
  "vehicle_number": "BUS-001",
  "status": "ONLINE",
  "route_id": 1
}
```

---

### Current Vehicle Location

```http
GET /api/me/vehicle/location
```

Returns the latest GPS location of the user's assigned vehicle.

Example:

```json
{
  "vehicle_id": 1,
  "latitude": 22.7196,
  "longitude": 75.8577,
  "speed": 35,
  "timestamp": "2026-09-09T12:00:00"
}
```

---

### Vehicle GPS History

```http
GET /api/me/vehicle/history
```

Returns historical GPS records for the authenticated user's assigned vehicle.

---

### Health Check

```http
GET /health
```

Response:

```json
{
  "status": "healthy"
}
```

---

### Database Test

```http
GET /db-test
```

Checks PostgreSQL connectivity.

---

##  Authorization

Protected endpoints use the authenticated JWT user.

The backend obtains the current user and uses their assigned `route_id` and `vehicle_id`.

Therefore:

```text
User A
   ↓
vehicle_id = 1
   ↓
BUS-001
```

while:

```text
User B
   ↓
vehicle_id = 2
   ↓
BUS-002
```

A user cannot simply provide another vehicle ID to access another user's vehicle through these `/api/me` endpoints.

---

##  Local Setup

### Prerequisites

Install:

* Python
* PostgreSQL
* MQTT broker
* Git

---

### Clone Repository

```bash
git clone https://github.com/tinachelwanii/vehicle-tracking-backend.git
cd vehicle-tracking-backend
```

---

### Create Virtual Environment

Windows:

```powershell
python -m venv venv
```

Activate:

```powershell
.\venv\Scripts\activate
```

---

### Install Dependencies

```powershell
pip install -r requirements.txt
```

---

## Environment Variables

Create a `.env` file:

```env
DATABASE_URL=postgresql://<username>:<password>@localhost:5432/vehicle_tracking

JWT_SECRET=<your-secret>
JWT_ALGORITHM=HS256

MQTT_HOST=localhost
MQTT_PORT=1883
```

**Do not commit `.env` to GitHub.**

---

##  Database Setup

Create a PostgreSQL database named:

```text
vehicle_tracking
```

The application creates the required tables using SQLAlchemy when the backend starts.

Seed the initial data using:

```powershell
python .\app\seed.py
```

---

##  Run Backend

Start FastAPI:

```powershell
uvicorn app.main:app --reload
```

The backend runs on:

```text
http://127.0.0.1:8000
```

Swagger API documentation:

```text
http://127.0.0.1:8000/docs
```

---

## 15. Testing Flow

1. Start PostgreSQL.
2. Start MQTT broker.
3. Start FastAPI backend.
4. Start GPS simulator.
5. Login through the Flutter application.
6. Backend returns JWT token.
7. Flutter requests assigned route and vehicle.
8. GPS simulator publishes vehicle locations through MQTT.
9. Backend stores GPS records in PostgreSQL.
10. Flutter periodically requests the latest location and history.
11. The map displays the assigned route and current vehicle position.

---

##  Example Test Users

### User A

```text
Email: usera@example.com
Password: password123
Route: Route A
Vehicle: BUS-001
```

### User B

```text
Email: userb@example.com
Password: password123
Route: Route B
Vehicle: BUS-002
```

These credentials are intended for local assessment/testing purposes.

---

##  Key Features

* JWT-based authentication
* Multiple users
* User-specific route assignment
* User-specific vehicle assignment
* MQTT-based GPS ingestion
* GPS data persistence
* Current vehicle location
* Historical GPS tracking
* Vehicle online status
* Protected APIs
* PostgreSQL database
* GPS simulator
* FastAPI Swagger documentation
* Modular backend architecture

---


##  Repository

Backend repository:

https://github.com/tinachelwanii/vehicle-tracking-backend
