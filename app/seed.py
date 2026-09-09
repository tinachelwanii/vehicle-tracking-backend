from sqlalchemy.orm import Session
from app.database import SessionLocal
from app.models import Route, Vehicle, User

from passlib.context import CryptContext


pwd_context = CryptContext(
    schemes=["bcrypt"],
    deprecated="auto"
)


def seed_database():
    db: Session = SessionLocal()

    try:
        # Check whether data already exists
        if db.query(Route).first():
            print("Database already contains data.")
            return

        # -------------------------
        # Create Routes
        # -------------------------

        route_a = Route(
            name="Route A",
            description="Indore to Vijay Nagar route",
            start_location="Indore",
            end_location="Vijay Nagar",
            route_coordinates="22.7196,75.8577;22.7533,75.8937"
        )

        route_b = Route(
            name="Route B",
            description="Bhopal to MP Nagar route",
            start_location="Bhopal",
            end_location="MP Nagar",
            route_coordinates="23.2599,77.4126;23.2330,77.4340"
        )

        db.add_all([route_a, route_b])
        db.commit()

        db.refresh(route_a)
        db.refresh(route_b)

        # -------------------------
        # Create Vehicles
        # -------------------------

        vehicle_a = Vehicle(
            vehicle_number="BUS-001",
            status="ONLINE",
            route_id=route_a.id
        )

        vehicle_b = Vehicle(
            vehicle_number="BUS-002",
            status="ONLINE",
            route_id=route_b.id
        )

        db.add_all([vehicle_a, vehicle_b])
        db.commit()

        db.refresh(vehicle_a)
        db.refresh(vehicle_b)

        # -------------------------
        # Create Users
        # -------------------------

        user_a = User(
            email="usera@example.com",
            password_hash=pwd_context.hash("password123"),
            route_id=route_a.id,
            vehicle_id=vehicle_a.id
        )

        user_b = User(
            email="userb@example.com",
            password_hash=pwd_context.hash("password123"),
            route_id=route_b.id,
            vehicle_id=vehicle_b.id
        )

        db.add_all([user_a, user_b])
        db.commit()

        print("Database seeded successfully!")
        print()
        print("User A:")
        print("Email: usera@example.com")
        print("Password: password123")
        print("Route: Route A")
        print("Vehicle: BUS-001")
        print()
        print("User B:")
        print("Email: userb@example.com")
        print("Password: password123")
        print("Route: Route B")
        print("Vehicle: BUS-002")

    except Exception as e:
        db.rollback()
        print("Error while seeding database:")
        print(e)

    finally:
        db.close()


if __name__ == "__main__":
    seed_database()