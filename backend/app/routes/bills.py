from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy import String, cast, desc, func, or_
from sqlalchemy.orm import Session

from app.dependencies import get_db
from app.dependencies_auth import get_current_user
from app.models.account import Account
from app.models.bill import Bill
from app.models.user import User
from app.schemas import MessageResponse, PaginatedResponse
from app.schemas.bill import BillCreate, BillResponse, BillUpdate
from app.utils import get_object_or_404

router = APIRouter()


@router.post("/", response_model=BillResponse, status_code=status.HTTP_201_CREATED)
def create_bill(
    bill_in: BillCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    account = db.query(Account).filter(Account.id == bill_in.account_id).first()
    if not account:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Account not found",
        )

    if current_user.role != "admin" and account.user_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not allowed to create bill for this account",
        )

    bill = Bill(
        account_id=bill_in.account_id,
        amount=bill_in.amount,
        due_date=bill_in.due_date,
        status=bill_in.status,
    )

    db.add(bill)
    db.commit()
    db.refresh(bill)
    return bill


@router.get("/", response_model=PaginatedResponse[BillResponse])
def list_bills(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
    skip: int = 0,
    limit: int = Query(10, le=100),
    account_id: Optional[int] = None,
    status_filter: Optional[str] = Query(default=None, alias="status"),
    search: Optional[str] = None,
):
    query = db.query(Bill).join(Account, Bill.account_id == Account.id)

    if current_user.role != "admin":
        query = query.filter(Account.user_id == current_user.id)

    if account_id is not None:
        query = query.filter(Bill.account_id == account_id)

    if status_filter:
        query = query.filter(Bill.status == status_filter)

    if search:
        query = query.filter(
            or_(
                Bill.status.ilike(f"%{search}%"),
                cast(Bill.amount, String).ilike(f"%{search}%"),
                cast(Bill.due_date, String).ilike(f"%{search}%"),
            )
        )

    total = query.with_entities(func.count(Bill.id)).scalar() or 0
    items = query.order_by(desc(Bill.created_at)).offset(skip).limit(limit).all()

    return PaginatedResponse[BillResponse](
        total=total,
        skip=skip,
        limit=limit,
        items=items,
    )


@router.get("/{bill_id}", response_model=BillResponse)
def get_bill(
    bill_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    bill = get_object_or_404(db, Bill, bill_id)
    account = get_object_or_404(db, Account, bill.account_id)

    if current_user.role != "admin" and account.user_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not allowed to view this bill",
        )

    return bill


@router.put("/{bill_id}", response_model=BillResponse)
def update_bill(
    bill_id: int,
    bill_in: BillUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    bill = get_object_or_404(db, Bill, bill_id)
    current_account = get_object_or_404(db, Account, bill.account_id)

    if current_user.role != "admin" and current_account.user_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not allowed to update this bill",
        )

    if bill_in.account_id is not None:
        new_account = db.query(Account).filter(Account.id == bill_in.account_id).first()
        if not new_account:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Account not found",
            )

        if current_user.role != "admin" and new_account.user_id != current_user.id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Not allowed to move bill to this account",
            )

        bill.account_id = bill_in.account_id

    if bill_in.amount is not None:
        bill.amount = bill_in.amount

    if bill_in.due_date is not None:
        bill.due_date = bill_in.due_date

    if bill_in.status is not None:
        bill.status = bill_in.status

    db.commit()
    db.refresh(bill)
    return bill


@router.delete("/{bill_id}", response_model=MessageResponse)
def delete_bill(
    bill_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    bill = get_object_or_404(db, Bill, bill_id)
    account = get_object_or_404(db, Account, bill.account_id)

    if current_user.role != "admin" and account.user_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not allowed to delete this bill",
        )

    db.delete(bill)
    db.commit()
    return MessageResponse(message="Bill deleted successfully")