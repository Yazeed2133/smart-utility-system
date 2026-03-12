from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from app.dependencies import get_db
from app.models.payment import Payment
from app.models.bill import Bill
from app.schemas.payment import PaymentCreate, PaymentUpdate, PaymentResponse
from app.schemas.common import MessageResponse, PaginatedResponse
from app.utils import get_object_or_404

router = APIRouter(
    prefix="/payments",
    tags=["Payments"]
)


@router.post("/", response_model=PaymentResponse)
def create_payment(payment: PaymentCreate, db: Session = Depends(get_db)):
    bill = db.query(Bill).filter(Bill.id == payment.bill_id).first()
    get_object_or_404(bill, "Bill not found")

    new_payment = Payment(
        bill_id=payment.bill_id,
        amount_paid=payment.amount_paid,
        payment_date=payment.payment_date,
        payment_method=payment.payment_method
    )
    db.add(new_payment)
    db.commit()
    db.refresh(new_payment)
    return new_payment


@router.get("/", response_model=PaginatedResponse[PaymentResponse])
def get_payments(
    bill_id: int | None = Query(None),
    skip: int = Query(0, ge=0),
    limit: int = Query(10, ge=1, le=100),
    db: Session = Depends(get_db)
):
    query = db.query(Payment)

    if bill_id is not None:
        query = query.filter(Payment.bill_id == bill_id)

    total = query.count()
    items = query.order_by(Payment.id.desc()).offset(skip).limit(limit).all()

    return {
        "total": total,
        "items": items
    }


@router.get("/{payment_id}", response_model=PaymentResponse)
def get_payment(payment_id: int, db: Session = Depends(get_db)):
    payment = db.query(Payment).filter(Payment.id == payment_id).first()
    payment = get_object_or_404(payment, "Payment not found")
    return payment


@router.put("/{payment_id}", response_model=PaymentResponse)
def update_payment(payment_id: int, payment_data: PaymentUpdate, db: Session = Depends(get_db)):
    payment = db.query(Payment).filter(Payment.id == payment_id).first()
    payment = get_object_or_404(payment, "Payment not found")

    bill = db.query(Bill).filter(Bill.id == payment_data.bill_id).first()
    get_object_or_404(bill, "Bill not found")

    payment.bill_id = payment_data.bill_id
    payment.amount_paid = payment_data.amount_paid
    payment.payment_date = payment_data.payment_date
    payment.payment_method = payment_data.payment_method

    db.commit()
    db.refresh(payment)
    return payment


@router.delete("/{payment_id}", response_model=MessageResponse)
def delete_payment(payment_id: int, db: Session = Depends(get_db)):
    payment = db.query(Payment).filter(Payment.id == payment_id).first()
    payment = get_object_or_404(payment, "Payment not found")

    db.delete(payment)
    db.commit()
    return {"message": "Payment deleted successfully"}