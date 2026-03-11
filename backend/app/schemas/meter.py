from pydantic import BaseModel


class MeterCreate(BaseModel):
    meter_number: str
    meter_type: str
    status: str = "active"
    account_id: int


class MeterUpdate(BaseModel):
    meter_number: str
    meter_type: str
    status: str = "active"
    account_id: int


class MeterResponse(BaseModel):
    id: int
    meter_number: str
    meter_type: str
    status: str
    account_id: int

    class Config:
        from_attributes = True