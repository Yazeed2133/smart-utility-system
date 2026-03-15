from datetime import date, datetime
from typing import Literal, Optional

from pydantic import BaseModel, ConfigDict, Field


class PaymentBase(BaseModel):
    bill_id: int
    amount: float = Field(gt=0)
    payment_method: Literal["cash", "card", "bank_transfer"]
    payment_date: date


class PaymentCreate(PaymentBase):
    pass


class PaymentUpdate(BaseModel):
    bill_id: Optional[int] = None
    amount: Optional[float] = Field(default=None, gt=0)
    payment_method: Optional[Literal["cash", "card", "bank_transfer"]] = None
    payment_date: Optional[date] = None


class PaymentResponse(PaymentBase):
    model_config = ConfigDict(from_attributes=True)

    id: int
    created_at: datetime
    updated_at: datetime