from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from app.dependencies import get_db
from app.models.bill import Bill
from app.models.account import Account
from app.schemas.bill import BillCreate, BillUpdate, BillResponse
from app.schemas.common import MessageResponse, PaginatedResponse
from app.utils import get_object_or_404

router = APIRouter(
    prefix="/bills",
    tags=["Bills"]
)


@router.post("/", response_model=BillResponse)
def create_bill(bill: BillCreate, db: Session = Depends(get_db)):
    account = db.query(Account).filter(Account.id == bill.account_id).first()
    get_object_or_404(account, "Account not found")

    new_bill = Bill(
        account_id=bill.account_id,
        amount=bill.amount,
        due_date=bill.due_date,
        status=bill.status
    )
    db.add(new_bill)
    db.commit()
    db.refresh(new_bill)
    return new_bill


@router.get("/", response_model=PaginatedResponse[BillResponse])
def get_bills(
    account_id: int | None = Query(None),
    skip: int = Query(0, ge=0),
    limit: int = Query(10, ge=1, le=100),
    db: Session = Depends(get_db)
):
    query = db.query(Bill)

    if account_id is not None:
        query = query.filter(Bill.account_id == account_id)

    total = query.count()
    items = query.order_by(Bill.id.desc()).offset(skip).limit(limit).all()

    return {
        "total": total,
        "items": items
    }


@router.get("/{bill_id}", response_model=BillResponse)
def get_bill(bill_id: int, db: Session = Depends(get_db)):
    bill = db.query(Bill).filter(Bill.id == bill_id).first()
    bill = get_object_or_404(bill, "Bill not found")
    return bill


@router.put("/{bill_id}", response_model=BillResponse)
def update_bill(bill_id: int, bill_data: BillUpdate, db: Session = Depends(get_db)):
    bill = db.query(Bill).filter(Bill.id == bill_id).first()
    bill = get_object_or_404(bill, "Bill not found")

    account = db.query(Account).filter(Account.id == bill_data.account_id).first()
    get_object_or_404(account, "Account not found")

    bill.account_id = bill_data.account_id
    bill.amount = bill_data.amount
    bill.due_date = bill_data.due_date
    bill.status = bill_data.status

    db.commit()
    db.refresh(bill)
    return bill


@router.delete("/{bill_id}", response_model=MessageResponse)
def delete_bill(bill_id: int, db: Session = Depends(get_db)):
    bill = db.query(Bill).filter(Bill.id == bill_id).first()
    bill = get_object_or_404(bill, "Bill not found")

    db.delete(bill)
    db.commit()
    return {"message": "Bill deleted successfully"}