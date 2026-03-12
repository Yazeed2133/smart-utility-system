from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from app.dependencies import get_db
from app.models.meter import Meter
from app.models.account import Account
from app.schemas.meter import MeterCreate, MeterUpdate, MeterResponse
from app.schemas.common import MessageResponse, PaginatedResponse
from app.utils import get_object_or_404

router = APIRouter(
    prefix="/meters",
    tags=["Meters"]
)


@router.post("/", response_model=MeterResponse)
def create_meter(meter: MeterCreate, db: Session = Depends(get_db)):
    account = db.query(Account).filter(Account.id == meter.account_id).first()
    get_object_or_404(account, "Account not found")

    existing_meter = db.query(Meter).filter(
        Meter.meter_number == meter.meter_number
    ).first()
    if existing_meter:
        raise HTTPException(status_code=400, detail="Meter number already exists")

    new_meter = Meter(
        account_id=meter.account_id,
        meter_number=meter.meter_number,
        meter_type=meter.meter_type,
        location=meter.location,
        installed_at=meter.installed_at
    )
    db.add(new_meter)
    db.commit()
    db.refresh(new_meter)
    return new_meter


@router.get("/", response_model=PaginatedResponse[MeterResponse])
def get_meters(
    account_id: int | None = Query(None),
    skip: int = Query(0, ge=0),
    limit: int = Query(10, ge=1, le=100),
    db: Session = Depends(get_db)
):
    query = db.query(Meter)

    if account_id is not None:
        query = query.filter(Meter.account_id == account_id)

    total = query.count()
    items = query.order_by(Meter.id.desc()).offset(skip).limit(limit).all()

    return {
        "total": total,
        "items": items
    }


@router.get("/{meter_id}", response_model=MeterResponse)
def get_meter(meter_id: int, db: Session = Depends(get_db)):
    meter = db.query(Meter).filter(Meter.id == meter_id).first()
    meter = get_object_or_404(meter, "Meter not found")
    return meter


@router.put("/{meter_id}", response_model=MeterResponse)
def update_meter(meter_id: int, meter_data: MeterUpdate, db: Session = Depends(get_db)):
    meter = db.query(Meter).filter(Meter.id == meter_id).first()
    meter = get_object_or_404(meter, "Meter not found")

    account = db.query(Account).filter(Account.id == meter_data.account_id).first()
    get_object_or_404(account, "Account not found")

    existing_meter = db.query(Meter).filter(
        Meter.meter_number == meter_data.meter_number,
        Meter.id != meter_id
    ).first()
    if existing_meter:
        raise HTTPException(status_code=400, detail="Meter number already exists")

    meter.account_id = meter_data.account_id
    meter.meter_number = meter_data.meter_number
    meter.meter_type = meter_data.meter_type
    meter.location = meter_data.location
    meter.installed_at = meter_data.installed_at

    db.commit()
    db.refresh(meter)
    return meter


@router.delete("/{meter_id}", response_model=MessageResponse)
def delete_meter(meter_id: int, db: Session = Depends(get_db)):
    meter = db.query(Meter).filter(Meter.id == meter_id).first()
    meter = get_object_or_404(meter, "Meter not found")

    db.delete(meter)
    db.commit()
    return {"message": "Meter deleted successfully"}