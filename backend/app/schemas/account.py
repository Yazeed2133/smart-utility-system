from datetime import datetime
from typing import Optional

from pydantic import BaseModel, ConfigDict, Field


class AccountBase(BaseModel):
    user_id: int
    account_number: str = Field(min_length=3, max_length=50)
    account_type: str = Field(min_length=2, max_length=50)
    address: str = Field(min_length=3, max_length=255)


class AccountCreate(AccountBase):
    pass


class AccountUpdate(BaseModel):
    user_id: Optional[int] = None
    account_number: Optional[str] = Field(default=None, min_length=3, max_length=50)
    account_type: Optional[str] = Field(default=None, min_length=2, max_length=50)
    address: Optional[str] = Field(default=None, min_length=3, max_length=255)


class AccountResponse(AccountBase):
    model_config = ConfigDict(from_attributes=True)

    id: int
    created_at: datetime
    updated_at: datetime