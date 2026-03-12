from pydantic import BaseModel
from datetime import datetime


class ReadingCreate(BaseModel):
    meter_id: int
    reading_value: float
    reading_date: datetime


class ReadingUpdate(BaseModel):
    meter_id: int
    reading_value: float
    reading_date: datetime


class ReadingResponse(BaseModel):
    id: int
    meter_id: int
    reading_value: float
    reading_date: datetime
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True