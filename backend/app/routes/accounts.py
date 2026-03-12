from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from app.dependencies import get_db
from app.models.account import Account
from app.models.user import User
from app.schemas.account import AccountCreate, AccountUpdate, AccountResponse
from app.schemas.common import MessageResponse, PaginatedResponse
from app.utils import get_object_or_404

router = APIRouter(
    prefix="/accounts",
    tags=["Accounts"]
)


@router.post("/", response_model=AccountResponse)
def create_account(account: AccountCreate, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.id == account.user_id).first()
    get_object_or_404(user, "User not found")

    existing_account = db.query(Account).filter(
        Account.account_number == account.account_number
    ).first()
    if existing_account:
        raise HTTPException(status_code=400, detail="Account number already exists")

    new_account = Account(
        user_id=account.user_id,
        account_number=account.account_number,
        account_type=account.account_type,
        balance=account.balance
    )
    db.add(new_account)
    db.commit()
    db.refresh(new_account)
    return new_account


@router.get("/", response_model=PaginatedResponse[AccountResponse])
def get_accounts(
    search: str | None = Query(None),
    user_id: int | None = Query(None),
    skip: int = Query(0, ge=0),
    limit: int = Query(10, ge=1, le=100),
    db: Session = Depends(get_db)
):
    query = db.query(Account)

    if search:
        query = query.filter(Account.account_number.ilike(f"%{search}%"))

    if user_id is not None:
        query = query.filter(Account.user_id == user_id)

    total = query.count()
    items = query.order_by(Account.id.desc()).offset(skip).limit(limit).all()

    return {
        "total": total,
        "items": items
    }


@router.get("/{account_id}", response_model=AccountResponse)
def get_account(account_id: int, db: Session = Depends(get_db)):
    account = db.query(Account).filter(Account.id == account_id).first()
    account = get_object_or_404(account, "Account not found")
    return account


@router.put("/{account_id}", response_model=AccountResponse)
def update_account(account_id: int, account_data: AccountUpdate, db: Session = Depends(get_db)):
    account = db.query(Account).filter(Account.id == account_id).first()
    account = get_object_or_404(account, "Account not found")

    user = db.query(User).filter(User.id == account_data.user_id).first()
    get_object_or_404(user, "User not found")

    existing_account = db.query(Account).filter(
        Account.account_number == account_data.account_number,
        Account.id != account_id
    ).first()
    if existing_account:
        raise HTTPException(status_code=400, detail="Account number already exists")

    account.user_id = account_data.user_id
    account.account_number = account_data.account_number
    account.account_type = account_data.account_type
    account.balance = account_data.balance

    db.commit()
    db.refresh(account)
    return account


@router.delete("/{account_id}", response_model=MessageResponse)
def delete_account(account_id: int, db: Session = Depends(get_db)):
    account = db.query(Account).filter(Account.id == account_id).first()
    account = get_object_or_404(account, "Account not found")

    db.delete(account)
    db.commit()
    return {"message": "Account deleted successfully"}