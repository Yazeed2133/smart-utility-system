from pydantic import BaseModel
from datetime import datetime


class ReadingCreate(BaseModel):
    reading_value: float
    meter_id: int


class ReadingUpdate(BaseModel):
    reading_value: float
    meter_id: int


class ReadingResponse(BaseModel):
    id: int
    reading_value: float
    reading_date: datetime
    meter_id: int

    class Config:
        from_attributes = True