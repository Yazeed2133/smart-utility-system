from pydantic import BaseModel
from datetime import datetime


class BillCreate(BaseModel):
    billing_month: str
    electricity_amount: float = 0.0
    water_amount: float = 0.0
    total_amount: float
    status: str = "unpaid"
    due_date: datetime
    account_id: int


class BillUpdate(BaseModel):
    billing_month: str
    electricity_amount: float = 0.0
    water_amount: float = 0.0
    total_amount: float
    status: str = "unpaid"
    due_date: datetime
    account_id: int


class BillResponse(BaseModel):
    id: int
    billing_month: str
    electricity_amount: float
    water_amount: float
    total_amount: float
    status: str
    due_date: datetime
    created_at: datetime
    account_id: int

    class Config:
        from_attributes = True