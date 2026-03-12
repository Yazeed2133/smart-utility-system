from pydantic import BaseModel
from datetime import datetime
from enum import Enum


class PaymentMethod(str, Enum):
    cash = "cash"
    card = "card"
    bank_transfer = "bank_transfer"


class PaymentCreate(BaseModel):
    bill_id: int
    amount_paid: float
    payment_date: datetime
    payment_method: PaymentMethod


class PaymentUpdate(BaseModel):
    bill_id: int
    amount_paid: float
    payment_date: datetime
    payment_method: PaymentMethod


class PaymentResponse(BaseModel):
    id: int
    bill_id: int
    amount_paid: float
    payment_date: datetime
    payment_method: PaymentMethod
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True