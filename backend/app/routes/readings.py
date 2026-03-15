from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy import String, cast, desc, func, or_
from sqlalchemy.orm import Session

from app.dependencies import get_db
from app.dependencies_auth import get_current_user
from app.models.account import Account
from app.models.meter import Meter
from app.models.reading import Reading
from app.models.user import User
from app.schemas import MessageResponse, PaginatedResponse
from app.schemas.reading import ReadingCreate, ReadingResponse, ReadingUpdate
from app.utils import get_object_or_404

router = APIRouter()


@router.post("/", response_model=ReadingResponse, status_code=status.HTTP_201_CREATED)
def create_reading(
    reading_in: ReadingCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    meter = db.query(Meter).filter(Meter.id == reading_in.meter_id).first()
    if not meter:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Meter not found",
        )

    account = get_object_or_404(db, Account, meter.account_id)

    if current_user.role != "admin" and account.user_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not allowed to create reading for this meter",
        )

    reading = Reading(
        meter_id=reading_in.meter_id,
        reading_value=reading_in.reading_value,
        reading_date=reading_in.reading_date,
    )

    db.add(reading)
    db.commit()
    db.refresh(reading)
    return reading


@router.get("/", response_model=PaginatedResponse[ReadingResponse])
def list_readings(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
    skip: int = 0,
    limit: int = Query(10, le=100),
    meter_id: Optional[int] = None,
    search: Optional[str] = None,
):
    query = (
        db.query(Reading)
        .join(Meter, Reading.meter_id == Meter.id)
        .join(Account, Meter.account_id == Account.id)
    )

    if current_user.role != "admin":
        query = query.filter(Account.user_id == current_user.id)

    if meter_id is not None:
        query = query.filter(Reading.meter_id == meter_id)

    if search:
        query = query.filter(
            or_(
                cast(Reading.reading_value, String).ilike(f"%{search}%"),
                cast(Reading.reading_date, String).ilike(f"%{search}%"),
            )
        )

    total = query.with_entities(func.count(Reading.id)).scalar() or 0
    items = query.order_by(desc(Reading.created_at)).offset(skip).limit(limit).all()

    return PaginatedResponse[ReadingResponse](
        total=total,
        skip=skip,
        limit=limit,
        items=items,
    )


@router.get("/{reading_id}", response_model=ReadingResponse)
def get_reading(
    reading_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    reading = get_object_or_404(db, Reading, reading_id)
    meter = get_object_or_404(db, Meter, reading.meter_id)
    account = get_object_or_404(db, Account, meter.account_id)

    if current_user.role != "admin" and account.user_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not allowed to view this reading",
        )

    return reading


@router.put("/{reading_id}", response_model=ReadingResponse)
def update_reading(
    reading_id: int,
    reading_in: ReadingUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    reading = get_object_or_404(db, Reading, reading_id)
    current_meter = get_object_or_404(db, Meter, reading.meter_id)
    current_account = get_object_or_404(db, Account, current_meter.account_id)

    if current_user.role != "admin" and current_account.user_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not allowed to update this reading",
        )

    if reading_in.meter_id is not None:
        new_meter = db.query(Meter).filter(Meter.id == reading_in.meter_id).first()
        if not new_meter:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Meter not found",
            )

        new_account = get_object_or_404(db, Account, new_meter.account_id)
        if current_user.role != "admin" and new_account.user_id != current_user.id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Not allowed to move reading to this meter",
            )

        reading.meter_id = reading_in.meter_id

    if reading_in.reading_value is not None:
        reading.reading_value = reading_in.reading_value

    if reading_in.reading_date is not None:
        reading.reading_date = reading_in.reading_date

    db.commit()
    db.refresh(reading)
    return reading


@router.delete("/{reading_id}", response_model=MessageResponse)
def delete_reading(
    reading_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    reading = get_object_or_404(db, Reading, reading_id)
    meter = get_object_or_404(db, Meter, reading.meter_id)
    account = get_object_or_404(db, Account, meter.account_id)

    if current_user.role != "admin" and account.user_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not allowed to delete this reading",
        )

    db.delete(reading)
    db.commit()
    return MessageResponse(message="Reading deleted successfully")