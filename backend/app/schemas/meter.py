from datetime import datetime
from typing import Literal, Optional

from pydantic import BaseModel, ConfigDict, Field


class MeterBase(BaseModel):
    account_id: int
    meter_number: str = Field(min_length=3, max_length=50)
    meter_type: Literal["electricity", "water", "gas"]


class MeterCreate(MeterBase):
    pass


class MeterUpdate(BaseModel):
    account_id: Optional[int] = None
    meter_number: Optional[str] = Field(default=None, min_length=3, max_length=50)
    meter_type: Optional[Literal["electricity", "water", "gas"]] = None


class MeterResponse(MeterBase):
    model_config = ConfigDict(from_attributes=True)

    id: int
    created_at: datetime
    updated_at: datetime