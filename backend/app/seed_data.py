from datetime import date

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
        user_1 = User(
            name="Aya User",
            email="aya@example.com",
            password_hash=hash_password("user123"),
            role="user",
        )
        user_2 = User(
            name="Omar User",
            email="omar@example.com",
            password_hash=hash_password("user123"),
            role="user",
        )

        db.add_all([admin_user, user_1, user_2])
        db.commit()
        db.refresh(admin_user)
        db.refresh(user_1)
        db.refresh(user_2)

        account_1 = Account(
            user_id=admin_user.id,
            account_number="ACC-1001",
            account_type="residential",
            address="Nicosia, North Cyprus",
        )
        account_2 = Account(
            user_id=user_1.id,
            account_number="ACC-1002",
            account_type="commercial",
            address="Kyrenia, North Cyprus",
        )
        account_3 = Account(
            user_id=user_2.id,
            account_number="ACC-1003",
            account_type="residential",
            address="Famagusta, North Cyprus",
        )

        db.add_all([account_1, account_2, account_3])
        db.commit()
        db.refresh(account_1)
        db.refresh(account_2)
        db.refresh(account_3)

        meter_1 = Meter(
            account_id=account_1.id,
            meter_number="MTR-1001",
            meter_type="electricity",
        )
        meter_2 = Meter(
            account_id=account_1.id,
            meter_number="MTR-1002",
            meter_type="water",
        )
        meter_3 = Meter(
            account_id=account_2.id,
            meter_number="MTR-1003",
            meter_type="gas",
        )
        meter_4 = Meter(
            account_id=account_3.id,
            meter_number="MTR-1004",
            meter_type="electricity",
        )

        db.add_all([meter_1, meter_2, meter_3, meter_4])
        db.commit()
        db.refresh(meter_1)
        db.refresh(meter_2)
        db.refresh(meter_3)
        db.refresh(meter_4)

        readings = [
            Reading(meter_id=meter_1.id, reading_value=250.5, reading_date=date(2026, 3, 1)),
            Reading(meter_id=meter_1.id, reading_value=275.0, reading_date=date(2026, 3, 10)),
            Reading(meter_id=meter_2.id, reading_value=120.0, reading_date=date(2026, 3, 2)),
            Reading(meter_id=meter_3.id, reading_value=90.0, reading_date=date(2026, 3, 5)),
            Reading(meter_id=meter_4.id, reading_value=310.0, reading_date=date(2026, 3, 7)),
        ]
        db.add_all(readings)
        db.commit()

        bill_1 = Bill(
            account_id=account_1.id,
            amount=80.0,
            due_date=date(2026, 3, 20),
            status="pending",
        )
        bill_2 = Bill(
            account_id=account_2.id,
            amount=150.0,
            due_date=date(2026, 3, 22),
            status="paid",
        )
        bill_3 = Bill(
            account_id=account_3.id,
            amount=65.0,
            due_date=date(2026, 3, 18),
            status="overdue",
        )
        bill_4 = Bill(
            account_id=account_1.id,
            amount=110.0,
            due_date=date(2026, 4, 5),
            status="pending",
        )

        db.add_all([bill_1, bill_2, bill_3, bill_4])
        db.commit()
        db.refresh(bill_1)
        db.refresh(bill_2)
        db.refresh(bill_3)
        db.refresh(bill_4)

        payments = [
            Payment(
                bill_id=bill_2.id,
                amount=150.0,
                payment_method="cash",
                payment_date=date(2026, 3, 10),
            ),
            Payment(
                bill_id=bill_3.id,
                amount=20.0,
                payment_method="card",
                payment_date=date(2026, 3, 12),
            ),
            Payment(
                bill_id=bill_1.id,
                amount=30.0,
                payment_method="bank_transfer",
                payment_date=date(2026, 3, 13),
            ),
        ]

        db.add_all(payments)
        db.commit()

        print("Seed data inserted successfully.")
        print("Admin login: admin@example.com / admin123")
        print("User login: aya@example.com / user123")
        print("User login: omar@example.com / user123")

    finally:
        db.close()


if __name__ == "__main__":
    seed_data()