from pydantic import BaseModel
from datetime import datetime


class PaymentCreate(BaseModel):
    amount: float
    payment_method: str
    payment_status: str = "completed"
    transaction_ref: str | None = None
    bill_id: int


class PaymentUpdate(BaseModel):
    amount: float
    payment_method: str
    payment_status: str = "completed"
    transaction_ref: str | None = None
    bill_id: int


class PaymentResponse(BaseModel):
    id: int
    amount: float
    payment_method: str
    payment_status: str
    transaction_ref: str | None = None
    paid_at: datetime
    bill_id: int

    class Config:
        from_attributes = True