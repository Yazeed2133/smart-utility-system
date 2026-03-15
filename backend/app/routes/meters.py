from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy import desc, func, or_
from sqlalchemy.orm import Session

from app.dependencies import get_db
from app.dependencies_auth import get_current_user
from app.models.account import Account
from app.models.meter import Meter
from app.models.user import User
from app.schemas import MessageResponse, PaginatedResponse
from app.schemas.meter import MeterCreate, MeterResponse, MeterUpdate
from app.utils import get_object_or_404

router = APIRouter()


@router.post("/", response_model=MeterResponse, status_code=status.HTTP_201_CREATED)
def create_meter(
    meter_in: MeterCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    account = db.query(Account).filter(Account.id == meter_in.account_id).first()
    if not account:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Account not found",
        )

    if current_user.role != "admin" and account.user_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not allowed to create meter for this account",
        )

    existing_meter = db.query(Meter).filter(Meter.meter_number == meter_in.meter_number).first()
    if existing_meter:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Meter number already exists",
        )

    meter = Meter(
        account_id=meter_in.account_id,
        meter_number=meter_in.meter_number,
        meter_type=meter_in.meter_type,
    )

    db.add(meter)
    db.commit()
    db.refresh(meter)
    return meter


@router.get("/", response_model=PaginatedResponse[MeterResponse])
def list_meters(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
    skip: int = 0,
    limit: int = Query(10, le=100),
    account_id: Optional[int] = None,
    meter_type: Optional[str] = None,
    search: Optional[str] = None,
):
    query = db.query(Meter).join(Account, Meter.account_id == Account.id)

    if current_user.role != "admin":
        query = query.filter(Account.user_id == current_user.id)

    if account_id is not None:
        query = query.filter(Meter.account_id == account_id)

    if meter_type:
        query = query.filter(Meter.meter_type == meter_type)

    if search:
        query = query.filter(
            or_(
                Meter.meter_number.ilike(f"%{search}%"),
                Meter.meter_type.ilike(f"%{search}%"),
            )
        )

    total = query.with_entities(func.count(Meter.id)).scalar() or 0
    items = query.order_by(desc(Meter.created_at)).offset(skip).limit(limit).all()

    return PaginatedResponse[MeterResponse](
        total=total,
        skip=skip,
        limit=limit,
        items=items,
    )


@router.get("/{meter_id}", response_model=MeterResponse)
def get_meter(
    meter_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    meter = get_object_or_404(db, Meter, meter_id)
    account = get_object_or_404(db, Account, meter.account_id)

    if current_user.role != "admin" and account.user_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not allowed to view this meter",
        )

    return meter


@router.put("/{meter_id}", response_model=MeterResponse)
def update_meter(
    meter_id: int,
    meter_in: MeterUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    meter = get_object_or_404(db, Meter, meter_id)
    current_account = get_object_or_404(db, Account, meter.account_id)

    if current_user.role != "admin" and current_account.user_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not allowed to update this meter",
        )

    if meter_in.account_id is not None:
        new_account = db.query(Account).filter(Account.id == meter_in.account_id).first()
        if not new_account:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Account not found",
            )

        if current_user.role != "admin" and new_account.user_id != current_user.id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Not allowed to move meter to this account",
            )

        meter.account_id = meter_in.account_id

    if meter_in.meter_number is not None and meter_in.meter_number != meter.meter_number:
        existing_meter = db.query(Meter).filter(Meter.meter_number == meter_in.meter_number).first()
        if existing_meter:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Meter number already exists",
            )
        meter.meter_number = meter_in.meter_number

    if meter_in.meter_type is not None:
        meter.meter_type = meter_in.meter_type

    db.commit()
    db.refresh(meter)
    return meter


@router.delete("/{meter_id}", response_model=MessageResponse)
def delete_meter(
    meter_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    meter = get_object_or_404(db, Meter, meter_id)
    account = get_object_or_404(db, Account, meter.account_id)

    if current_user.role != "admin" and account.user_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not allowed to delete this meter",
        )

    db.delete(meter)
    db.commit()
    return MessageResponse(message="Meter deleted successfully")