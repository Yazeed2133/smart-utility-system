from pydantic import BaseModel
from datetime import datetime


class AccountCreate(BaseModel):
    user_id: int
    account_number: str
    account_type: str
    balance: float


class AccountUpdate(BaseModel):
    user_id: int
    account_number: str
    account_type: str
    balance: float


class AccountResponse(BaseModel):
    id: int
    user_id: int
    account_number: str
    account_type: str
    balance: float
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True