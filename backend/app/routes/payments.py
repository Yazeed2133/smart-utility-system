from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy import String, cast, desc, func, or_
from sqlalchemy.orm import Session

from app.dependencies import get_db
from app.dependencies_auth import get_current_user
from app.models.account import Account
from app.models.bill import Bill
from app.models.payment import Payment
from app.models.user import User
from app.schemas import MessageResponse, PaginatedResponse
from app.schemas.payment import PaymentCreate, PaymentResponse, PaymentUpdate
from app.utils import get_object_or_404

router = APIRouter()


@router.post("/", response_model=PaymentResponse, status_code=status.HTTP_201_CREATED)
def create_payment(
    payment_in: PaymentCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    bill = db.query(Bill).filter(Bill.id == payment_in.bill_id).first()
    if not bill:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Bill not found",
        )

    account = get_object_or_404(db, Account, bill.account_id)

    if current_user.role != "admin" and account.user_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not allowed to create payment for this bill",
        )

    payment = Payment(
        bill_id=payment_in.bill_id,
        amount=payment_in.amount,
        payment_method=payment_in.payment_method,
        payment_date=payment_in.payment_date,
    )

    db.add(payment)
    db.commit()
    db.refresh(payment)
    return payment


@router.get("/", response_model=PaginatedResponse[PaymentResponse])
def list_payments(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
    skip: int = 0,
    limit: int = Query(10, le=100),
    bill_id: Optional[int] = None,
    payment_method: Optional[str] = None,
    search: Optional[str] = None,
):
    query = (
        db.query(Payment)
        .join(Bill, Payment.bill_id == Bill.id)
        .join(Account, Bill.account_id == Account.id)
    )

    if current_user.role != "admin":
        query = query.filter(Account.user_id == current_user.id)

    if bill_id is not None:
        query = query.filter(Payment.bill_id == bill_id)

    if payment_method:
        query = query.filter(Payment.payment_method == payment_method)

    if search:
        query = query.filter(
            or_(
                Payment.payment_method.ilike(f"%{search}%"),
                cast(Payment.amount, String).ilike(f"%{search}%"),
                cast(Payment.payment_date, String).ilike(f"%{search}%"),
            )
        )

    total = query.with_entities(func.count(Payment.id)).scalar() or 0
    items = query.order_by(desc(Payment.created_at)).offset(skip).limit(limit).all()

    return PaginatedResponse[PaymentResponse](
        total=total,
        skip=skip,
        limit=limit,
        items=items,
    )


@router.get("/{payment_id}", response_model=PaymentResponse)
def get_payment(
    payment_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    payment = get_object_or_404(db, Payment, payment_id)
    bill = get_object_or_404(db, Bill, payment.bill_id)
    account = get_object_or_404(db, Account, bill.account_id)

    if current_user.role != "admin" and account.user_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not allowed to view this payment",
        )

    return payment


@router.put("/{payment_id}", response_model=PaymentResponse)
def update_payment(
    payment_id: int,
    payment_in: PaymentUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    payment = get_object_or_404(db, Payment, payment_id)
    current_bill = get_object_or_404(db, Bill, payment.bill_id)
    current_account = get_object_or_404(db, Account, current_bill.account_id)

    if current_user.role != "admin" and current_account.user_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not allowed to update this payment",
        )

    if payment_in.bill_id is not None:
        new_bill = db.query(Bill).filter(Bill.id == payment_in.bill_id).first()
        if not new_bill:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Bill not found",
            )

        new_account = get_object_or_404(db, Account, new_bill.account_id)
        if current_user.role != "admin" and new_account.user_id != current_user.id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Not allowed to move payment to this bill",
            )

        payment.bill_id = payment_in.bill_id

    if payment_in.amount is not None:
        payment.amount = payment_in.amount

    if payment_in.payment_method is not None:
        payment.payment_method = payment_in.payment_method

    if payment_in.payment_date is not None:
        payment.payment_date = payment_in.payment_date

    db.commit()
    db.refresh(payment)
    return payment


@router.delete("/{payment_id}", response_model=MessageResponse)
def delete_payment(
    payment_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    payment = get_object_or_404(db, Payment, payment_id)
    bill = get_object_or_404(db, Bill, payment.bill_id)
    account = get_object_or_404(db, Account, bill.account_id)

    if current_user.role != "admin" and account.user_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not allowed to delete this payment",
        )

    db.delete(payment)
    db.commit()
    return MessageResponse(message="Payment deleted successfully")