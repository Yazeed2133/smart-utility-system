from app.database import Base, SessionLocal, engine
from app.models.account import Account
from app.models.bill import Bill
from app.models.meter import Meter
from app.models.payment import Payment
from app.models.reading import Reading
from app.models.user import User
from app.security import hash_password


def seed_data():
    Base.metadata.create_all(bind=engine)

    db = SessionLocal()

    try:
        if db.query(User).first():
            print("Seed skipped: data already exists.")
            return

        admin_user = User(
            name="Admin User",
            email="admin@example.com",
            password_hash=hash_password("admin123"),
            role="admin",
        )

        normal_user = User(
            name="Test User",
            email="user@example.com",
            password_hash=hash_password("user123"),
            role="user",
        )

        db.add_all([admin_user, normal_user])
        db.commit()
        db.refresh(admin_user)
        db.refresh(normal_user)

        account_1 = Account(
            user_id=admin_user.id,
            account_number="ACC-1001",
            account_type="residential",
            address="Nicosia, North Cyprus",
        )

        account_2 = Account(
            user_id=normal_user.id,
            account_number="ACC-1002",
            account_type="commercial",
            address="Kyrenia, North Cyprus",
        )

        db.add_all([account_1, account_2])
        db.commit()
        db.refresh(account_1)
        db.refresh(account_2)

        meter_1 = Meter(
            account_id=account_1.id,
            meter_number="MTR-1001",
            meter_type="electricity",
        )

        meter_2 = Meter(
            account_id=account_2.id,
            meter_number="MTR-1002",
            meter_type="water",
        )

        db.add_all([meter_1, meter_2])
        db.commit()
        db.refresh(meter_1)
        db.refresh(meter_2)

        reading_1 = Reading(
            meter_id=meter_1.id,
            reading_value=250.5,
            reading_date="2026-03-01",
        )

        reading_2 = Reading(
            meter_id=meter_2.id,
            reading_value=120.0,
            reading_date="2026-03-02",
        )

        db.add_all([reading_1, reading_2])
        db.commit()

        bill_1 = Bill(
            account_id=account_1.id,
            amount=80.0,
            due_date="2026-03-20",
            status="pending",
        )

        bill_2 = Bill(
            account_id=account_2.id,
            amount=150.0,
            due_date="2026-03-22",
            status="paid",
        )

        db.add_all([bill_1, bill_2])
        db.commit()
        db.refresh(bill_1)
        db.refresh(bill_2)

        payment_1 = Payment(
            bill_id=bill_2.id,
            amount=150.0,
            payment_method="cash",
            payment_date="2026-03-10",
        )

        db.add(payment_1)
        db.commit()

        print("Seed data inserted successfully.")
        print("Admin login: admin@example.com / admin123")
        print("User login: user@example.com / user123")

    finally:
        db.close()


if __name__ == "__main__":
    seed_data()