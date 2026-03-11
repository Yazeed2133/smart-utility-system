from pydantic import BaseModel


class AccountCreate(BaseModel):
    account_number: str
    address: str
    status: str = "active"
    user_id: int


class AccountUpdate(BaseModel):
    account_number: str
    address: str
    status: str = "active"
    user_id: int


class AccountResponse(BaseModel):
    id: int
    account_number: str
    address: str
    status: str
    user_id: int

    class Config:
        from_attributes = True