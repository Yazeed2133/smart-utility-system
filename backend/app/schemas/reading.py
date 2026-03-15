from datetime import date, datetime
from typing import Optional

from pydantic import BaseModel, ConfigDict, Field


class ReadingBase(BaseModel):
    meter_id: int
    reading_value: float = Field(gt=0)
    reading_date: date


class ReadingCreate(ReadingBase):
    pass


class ReadingUpdate(BaseModel):
    meter_id: Optional[int] = None
    reading_value: Optional[float] = Field(default=None, gt=0)
    reading_date: Optional[date] = None


class ReadingResponse(ReadingBase):
    model_config = ConfigDict(from_attributes=True)

    id: int
    created_at: datetime
    updated_at: datetime