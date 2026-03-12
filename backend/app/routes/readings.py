from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from app.dependencies import get_db
from app.models.reading import Reading
from app.models.meter import Meter
from app.schemas.reading import ReadingCreate, ReadingUpdate, ReadingResponse
from app.schemas.common import MessageResponse, PaginatedResponse
from app.utils import get_object_or_404

router = APIRouter(
    prefix="/readings",
    tags=["Readings"]
)


@router.post("/", response_model=ReadingResponse)
def create_reading(reading: ReadingCreate, db: Session = Depends(get_db)):
    meter = db.query(Meter).filter(Meter.id == reading.meter_id).first()
    get_object_or_404(meter, "Meter not found")

    new_reading = Reading(
        meter_id=reading.meter_id,
        reading_value=reading.reading_value,
        reading_date=reading.reading_date
    )
    db.add(new_reading)
    db.commit()
    db.refresh(new_reading)
    return new_reading


@router.get("/", response_model=PaginatedResponse[ReadingResponse])
def get_readings(
    meter_id: int | None = Query(None),
    skip: int = Query(0, ge=0),
    limit: int = Query(10, ge=1, le=100),
    db: Session = Depends(get_db)
):
    query = db.query(Reading)

    if meter_id is not None:
        query = query.filter(Reading.meter_id == meter_id)

    total = query.count()
    items = query.order_by(Reading.id.desc()).offset(skip).limit(limit).all()

    return {
        "total": total,
        "items": items
    }


@router.get("/{reading_id}", response_model=ReadingResponse)
def get_reading(reading_id: int, db: Session = Depends(get_db)):
    reading = db.query(Reading).filter(Reading.id == reading_id).first()
    reading = get_object_or_404(reading, "Reading not found")
    return reading


@router.put("/{reading_id}", response_model=ReadingResponse)
def update_reading(reading_id: int, reading_data: ReadingUpdate, db: Session = Depends(get_db)):
    reading = db.query(Reading).filter(Reading.id == reading_id).first()
    reading = get_object_or_404(reading, "Reading not found")

    meter = db.query(Meter).filter(Meter.id == reading_data.meter_id).first()
    get_object_or_404(meter, "Meter not found")

    reading.meter_id = reading_data.meter_id
    reading.reading_value = reading_data.reading_value
    reading.reading_date = reading_data.reading_date

    db.commit()
    db.refresh(reading)
    return reading


@router.delete("/{reading_id}", response_model=MessageResponse)
def delete_reading(reading_id: int, db: Session = Depends(get_db)):
    reading = db.query(Reading).filter(Reading.id == reading_id).first()
    reading = get_object_or_404(reading, "Reading not found")

    db.delete(reading)
    db.commit()
    return {"message": "Reading deleted successfully"}