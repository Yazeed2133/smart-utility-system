from fastapi import FastAPI, Depends, HTTPException
from sqlalchemy.orm import Session

from app.database import Base, engine, get_db


from app.models import User, Account, Meter, Reading, Bill, Payment
from app.schemas import (
    UserCreate, UserUpdate, UserResponse,
    AccountCreate, AccountUpdate, AccountResponse,
    MeterCreate, MeterUpdate, MeterResponse,
    ReadingCreate, ReadingUpdate, ReadingResponse,
    BillCreate, BillUpdate, BillResponse,
    PaymentCreate, PaymentUpdate, PaymentResponse
)


app = FastAPI()

Base.metadata.create_all(bind=engine)


@app.get("/")
def home():
    return {"message": "Smart Utility System is running"}


@app.post("/users", response_model=UserResponse)
def create_user(user: UserCreate, db: Session = Depends(get_db)):
    new_user = User(
        full_name=user.full_name,
        email=user.email,
        phone=user.phone,
        password=user.password,
        role=user.role
    )

    db.add(new_user)
    db.commit()
    db.refresh(new_user)

    return new_user


@app.get("/users", response_model=list[UserResponse])
def get_users(db: Session = Depends(get_db)):
    users = db.query(User).all()
    return users


@app.get("/users/{user_id}", response_model=UserResponse)
def get_user(user_id: int, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.id == user_id).first()

    if user is None:
        raise HTTPException(status_code=404, detail="User not found")

    return user


@app.delete("/users/{user_id}")
def delete_user(user_id: int, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.id == user_id).first()

    if user is None:
        raise HTTPException(status_code=404, detail="User not found")

    db.delete(user)
    db.commit()

    return {"message": "User deleted successfully"}


@app.put("/users/{user_id}", response_model=UserResponse)
def update_user(user_id: int, user_data: UserUpdate, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.id == user_id).first()

    if user is None:
        raise HTTPException(status_code=404, detail="User not found")

    user.full_name = user_data.full_name
    user.email = user_data.email
    user.phone = user_data.phone
    user.password = user_data.password
    user.role = user_data.role

    db.commit()
    db.refresh(user)

    return user



@app.post("/accounts", response_model=AccountResponse)
def create_account(account: AccountCreate, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.id == account.user_id).first()

    if user is None:
        raise HTTPException(status_code=404, detail="User not found")

    new_account = Account(
        account_number=account.account_number,
        address=account.address,
        status=account.status,
        user_id=account.user_id
    )

    db.add(new_account)
    db.commit()
    db.refresh(new_account)

    return new_account


@app.get("/accounts", response_model=list[AccountResponse])
def get_accounts(db: Session = Depends(get_db)):
    accounts = db.query(Account).all()
    return accounts



@app.get("/accounts/{account_id}", response_model=AccountResponse)
def get_account(account_id: int, db: Session = Depends(get_db)):
    account = db.query(Account).filter(Account.id == account_id).first()

    if account is None:
        raise HTTPException(status_code=404, detail="Account not found")

    return account


@app.put("/accounts/{account_id}", response_model=AccountResponse)
def update_account(account_id: int, account_data: AccountUpdate, db: Session = Depends(get_db)):
    account = db.query(Account).filter(Account.id == account_id).first()

    if account is None:
        raise HTTPException(status_code=404, detail="Account not found")

    user = db.query(User).filter(User.id == account_data.user_id).first()
    if user is None:
        raise HTTPException(status_code=404, detail="User not found")

    account.account_number = account_data.account_number
    account.address = account_data.address
    account.status = account_data.status
    account.user_id = account_data.user_id

    db.commit()
    db.refresh(account)

    return account


@app.delete("/accounts/{account_id}")
def delete_account(account_id: int, db: Session = Depends(get_db)):
    account = db.query(Account).filter(Account.id == account_id).first()

    if account is None:
        raise HTTPException(status_code=404, detail="Account not found")

    db.delete(account)
    db.commit()

    return {"message": "Account deleted successfully"}


@app.post("/meters", response_model=MeterResponse)
def create_meter(meter: MeterCreate, db: Session = Depends(get_db)):
    account = db.query(Account).filter(Account.id == meter.account_id).first()

    if account is None:
        raise HTTPException(status_code=404, detail="Account not found")

    new_meter = Meter(
        meter_number=meter.meter_number,
        meter_type=meter.meter_type,
        status=meter.status,
        account_id=meter.account_id
    )

    db.add(new_meter)
    db.commit()
    db.refresh(new_meter)

    return new_meter


@app.get("/meters", response_model=list[MeterResponse])
def get_meters(db: Session = Depends(get_db)):
    meters = db.query(Meter).all()
    return meters


@app.get("/meters/{meter_id}", response_model=MeterResponse)
def get_meter(meter_id: int, db: Session = Depends(get_db)):
    meter = db.query(Meter).filter(Meter.id == meter_id).first()

    if meter is None:
        raise HTTPException(status_code=404, detail="Meter not found")

    return meter


@app.put("/meters/{meter_id}", response_model=MeterResponse)
def update_meter(meter_id: int, meter_data: MeterUpdate, db: Session = Depends(get_db)):
    meter = db.query(Meter).filter(Meter.id == meter_id).first()

    if meter is None:
        raise HTTPException(status_code=404, detail="Meter not found")

    account = db.query(Account).filter(Account.id == meter_data.account_id).first()
    if account is None:
        raise HTTPException(status_code=404, detail="Account not found")

    meter.meter_number = meter_data.meter_number
    meter.meter_type = meter_data.meter_type
    meter.status = meter_data.status
    meter.account_id = meter_data.account_id

    db.commit()
    db.refresh(meter)

    return meter


@app.delete("/meters/{meter_id}")
def delete_meter(meter_id: int, db: Session = Depends(get_db)):
    meter = db.query(Meter).filter(Meter.id == meter_id).first()

    if meter is None:
        raise HTTPException(status_code=404, detail="Meter not found")

    db.delete(meter)
    db.commit()

    return {"message": "Meter deleted successfully"}


@app.post("/readings", response_model=ReadingResponse)
def create_reading(reading: ReadingCreate, db: Session = Depends(get_db)):
    meter = db.query(Meter).filter(Meter.id == reading.meter_id).first()

    if meter is None:
        raise HTTPException(status_code=404, detail="Meter not found")

    new_reading = Reading(
        reading_value=reading.reading_value,
        meter_id=reading.meter_id
    )

    db.add(new_reading)
    db.commit()
    db.refresh(new_reading)

    return new_reading


@app.get("/readings", response_model=list[ReadingResponse])
def get_readings(db: Session = Depends(get_db)):
    readings = db.query(Reading).all()
    return readings


@app.get("/readings/{reading_id}", response_model=ReadingResponse)
def get_reading(reading_id: int, db: Session = Depends(get_db)):
    reading = db.query(Reading).filter(Reading.id == reading_id).first()

    if reading is None:
        raise HTTPException(status_code=404, detail="Reading not found")

    return reading


@app.put("/readings/{reading_id}", response_model=ReadingResponse)
def update_reading(reading_id: int, reading_data: ReadingUpdate, db: Session = Depends(get_db)):
    reading = db.query(Reading).filter(Reading.id == reading_id).first()

    if reading is None:
        raise HTTPException(status_code=404, detail="Reading not found")

    meter = db.query(Meter).filter(Meter.id == reading_data.meter_id).first()
    if meter is None:
        raise HTTPException(status_code=404, detail="Meter not found")

    reading.reading_value = reading_data.reading_value
    reading.meter_id = reading_data.meter_id

    db.commit()
    db.refresh(reading)

    return reading


@app.delete("/readings/{reading_id}")
def delete_reading(reading_id: int, db: Session = Depends(get_db)):
    reading = db.query(Reading).filter(Reading.id == reading_id).first()

    if reading is None:
        raise HTTPException(status_code=404, detail="Reading not found")

    db.delete(reading)
    db.commit()

    return {"message": "Reading deleted successfully"}


@app.post("/bills", response_model=BillResponse)
def create_bill(bill: BillCreate, db: Session = Depends(get_db)):
    account = db.query(Account).filter(Account.id == bill.account_id).first()

    if account is None:
        raise HTTPException(status_code=404, detail="Account not found")

    new_bill = Bill(
        billing_month=bill.billing_month,
        electricity_amount=bill.electricity_amount,
        water_amount=bill.water_amount,
        total_amount=bill.total_amount,
        status=bill.status,
        due_date=bill.due_date,
        account_id=bill.account_id
    )

    db.add(new_bill)
    db.commit()
    db.refresh(new_bill)

    return new_bill

@app.get("/bills", response_model=list[BillResponse])
def get_bills(db: Session = Depends(get_db)):
    bills = db.query(Bill).all()
    return bills

@app.get("/bills/{bill_id}", response_model=BillResponse)
def get_bill(bill_id: int, db: Session = Depends(get_db)):
    bill = db.query(Bill).filter(Bill.id == bill_id).first()

    if bill is None:
        raise HTTPException(status_code=404, detail="Bill not found")

    return bill


@app.put("/bills/{bill_id}", response_model=BillResponse)
def update_bill(bill_id: int, bill_data: BillUpdate, db: Session = Depends(get_db)):
    bill = db.query(Bill).filter(Bill.id == bill_id).first()

    if bill is None:
        raise HTTPException(status_code=404, detail="Bill not found")

    account = db.query(Account).filter(Account.id == bill_data.account_id).first()
    if account is None:
        raise HTTPException(status_code=404, detail="Account not found")

    bill.billing_month = bill_data.billing_month
    bill.electricity_amount = bill_data.electricity_amount
    bill.water_amount = bill_data.water_amount
    bill.total_amount = bill_data.total_amount
    bill.status = bill_data.status
    bill.due_date = bill_data.due_date
    bill.account_id = bill_data.account_id

    db.commit()
    db.refresh(bill)

    return bill


@app.delete("/bills/{bill_id}")
def delete_bill(bill_id: int, db: Session = Depends(get_db)):
    bill = db.query(Bill).filter(Bill.id == bill_id).first()

    if bill is None:
        raise HTTPException(status_code=404, detail="Bill not found")

    db.delete(bill)
    db.commit()

    return {"message": "Bill deleted successfully"}


@app.post("/payments", response_model=PaymentResponse)
def create_payment(payment: PaymentCreate, db: Session = Depends(get_db)):
    bill = db.query(Bill).filter(Bill.id == payment.bill_id).first()

    if bill is None:
        raise HTTPException(status_code=404, detail="Bill not found")

    new_payment = Payment(
        amount=payment.amount,
        payment_method=payment.payment_method,
        payment_status=payment.payment_status,
        transaction_ref=payment.transaction_ref,
        bill_id=payment.bill_id
    )

    db.add(new_payment)

    if payment.payment_status == "completed":
        bill.status = "paid"

    db.commit()
    db.refresh(new_payment)

    return new_payment

@app.get("/payments", response_model=list[PaymentResponse])
def get_payments(db: Session = Depends(get_db)):
    payments = db.query(Payment).all()
    return payments


@app.get("/payments/{payment_id}", response_model=PaymentResponse)
def get_payment(payment_id: int, db: Session = Depends(get_db)):
    payment = db.query(Payment).filter(Payment.id == payment_id).first()

    if payment is None:
        raise HTTPException(status_code=404, detail="Payment not found")

    return payment


@app.put("/payments/{payment_id}", response_model=PaymentResponse)
def update_payment(payment_id: int, payment_data: PaymentUpdate, db: Session = Depends(get_db)):
    payment = db.query(Payment).filter(Payment.id == payment_id).first()

    if payment is None:
        raise HTTPException(status_code=404, detail="Payment not found")

    bill = db.query(Bill).filter(Bill.id == payment_data.bill_id).first()
    if bill is None:
        raise HTTPException(status_code=404, detail="Bill not found")

    payment.amount = payment_data.amount
    payment.payment_method = payment_data.payment_method
    payment.payment_status = payment_data.payment_status
    payment.transaction_ref = payment_data.transaction_ref
    payment.bill_id = payment_data.bill_id

    if payment_data.payment_status == "completed":
        bill.status = "paid"
    else:
        bill.status = "unpaid"

    db.commit()
    db.refresh(payment)

    return payment


@app.delete("/payments/{payment_id}")
def delete_payment(payment_id: int, db: Session = Depends(get_db)):
    payment = db.query(Payment).filter(Payment.id == payment_id).first()

    if payment is None:
        raise HTTPException(status_code=404, detail="Payment not found")

    db.delete(payment)
    db.commit()

    return {"message": "Payment deleted successfully"}