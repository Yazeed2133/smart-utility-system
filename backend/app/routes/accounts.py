from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy import desc, func, or_
from sqlalchemy.orm import Session

from app.dependencies import get_db
from app.dependencies_auth import get_current_user
from app.models.account import Account
from app.models.user import User
from app.schemas import MessageResponse, PaginatedResponse
from app.schemas.account import AccountCreate, AccountResponse, AccountUpdate
from app.utils import get_object_or_404

router = APIRouter()


@router.post("/", response_model=AccountResponse, status_code=status.HTTP_201_CREATED)
def create_account(
    account_in: AccountCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    user = db.query(User).filter(User.id == account_in.user_id).first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="User not found",
        )

    if current_user.role != "admin" and account_in.user_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You can only create accounts for yourself",
        )

    existing_account = db.query(Account).filter(Account.account_number == account_in.account_number).first()
    if existing_account:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Account number already exists",
        )

    account = Account(
        user_id=account_in.user_id,
        account_number=account_in.account_number,
        account_type=account_in.account_type,
        address=account_in.address,
    )

    db.add(account)
    db.commit()
    db.refresh(account)
    return account


@router.get("/", response_model=PaginatedResponse[AccountResponse])
def list_accounts(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
    skip: int = 0,
    limit: int = Query(10, le=100),
    search: Optional[str] = None,
    user_id: Optional[int] = None,
):
    query = db.query(Account)

    if current_user.role != "admin":
        query = query.filter(Account.user_id == current_user.id)
    elif user_id is not None:
        query = query.filter(Account.user_id == user_id)

    if search:
        query = query.filter(
            or_(
                Account.account_number.ilike(f"%{search}%"),
                Account.account_type.ilike(f"%{search}%"),
                Account.address.ilike(f"%{search}%"),
            )
        )

    total = query.with_entities(func.count(Account.id)).scalar() or 0
    items = query.order_by(desc(Account.created_at)).offset(skip).limit(limit).all()

    return PaginatedResponse[AccountResponse](
        total=total,
        skip=skip,
        limit=limit,
        items=items,
    )


@router.get("/{account_id}", response_model=AccountResponse)
def get_account(
    account_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    account = get_object_or_404(db, Account, account_id)

    if current_user.role != "admin" and account.user_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not allowed to view this account",
        )

    return account


@router.put("/{account_id}", response_model=AccountResponse)
def update_account(
    account_id: int,
    account_in: AccountUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    account = get_object_or_404(db, Account, account_id)

    if current_user.role != "admin" and account.user_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not allowed to update this account",
        )

    if account_in.user_id is not None:
        user = db.query(User).filter(User.id == account_in.user_id).first()
        if not user:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="User not found",
            )

        if current_user.role != "admin" and account_in.user_id != current_user.id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="You can only keep the account under yourself",
            )

        account.user_id = account_in.user_id

    if account_in.account_number is not None and account_in.account_number != account.account_number:
        existing_account = db.query(Account).filter(Account.account_number == account_in.account_number).first()
        if existing_account:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Account number already exists",
            )
        account.account_number = account_in.account_number

    if account_in.account_type is not None:
        account.account_type = account_in.account_type

    if account_in.address is not None:
        account.address = account_in.address

    db.commit()
    db.refresh(account)
    return account


@router.delete("/{account_id}", response_model=MessageResponse)
def delete_account(
    account_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    account = get_object_or_404(db, Account, account_id)

    if current_user.role != "admin" and account.user_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not allowed to delete this account",
        )

    db.delete(account)
    db.commit()
    return MessageResponse(message="Account deleted successfully")