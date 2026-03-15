from datetime import date, datetime
from typing import Literal, Optional

from pydantic import BaseModel, ConfigDict, Field


class BillBase(BaseModel):
    account_id: int
    amount: float = Field(gt=0)
    due_date: date
    status: Literal["pending", "paid", "overdue"]


class BillCreate(BillBase):
    pass


class BillUpdate(BaseModel):
    account_id: Optional[int] = None
    amount: Optional[float] = Field(default=None, gt=0)
    due_date: Optional[date] = None
    status: Optional[Literal["pending", "paid", "overdue"]] = None


class BillResponse(BillBase):
    model_config = ConfigDict(from_attributes=True)

    id: int
    created_at: datetime
    updated_at: datetime