from pydantic import BaseModel
from datetime import datetime
from enum import Enum


class BillStatus(str, Enum):
    pending = "pending"
    paid = "paid"
    overdue = "overdue"


class BillCreate(BaseModel):
    account_id: int
    amount: float
    due_date: datetime
    status: BillStatus


class BillUpdate(BaseModel):
    account_id: int
    amount: float
    due_date: datetime
    status: BillStatus


class BillResponse(BaseModel):
    id: int
    account_id: int
    amount: float
    due_date: datetime
    status: BillStatus
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True