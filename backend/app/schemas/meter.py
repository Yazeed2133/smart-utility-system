from pydantic import BaseModel
from datetime import datetime


class MeterCreate(BaseModel):
    account_id: int
    meter_number: str
    meter_type: str
    location: str
    installed_at: datetime


class MeterUpdate(BaseModel):
    account_id: int
    meter_number: str
    meter_type: str
    location: str
    installed_at: datetime


class MeterResponse(BaseModel):
    id: int
    account_id: int
    meter_number: str
    meter_type: str
    location: str
    installed_at: datetime
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True