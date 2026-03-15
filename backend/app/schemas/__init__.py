from typing import Generic, List, TypeVar

from pydantic import BaseModel

from app.schemas.account import AccountCreate, AccountResponse, AccountUpdate
from app.schemas.auth import (
    AuthMessageResponse,
    ChangePasswordRequest,
    LoginRequest,
    TokenResponse,
)
from app.schemas.bill import BillCreate, BillResponse, BillUpdate
from app.schemas.meter import MeterCreate, MeterResponse, MeterUpdate
from app.schemas.payment import PaymentCreate, PaymentResponse, PaymentUpdate
from app.schemas.reading import ReadingCreate, ReadingResponse, ReadingUpdate
from app.schemas.user import UserCreate, UserResponse, UserUpdate

T = TypeVar("T")


class MessageResponse(BaseModel):
    message: str


class PaginatedResponse(BaseModel, Generic[T]):
    total: int
    skip: int
    limit: int
    items: List[T]


__all__ = [
    "MessageResponse",
    "PaginatedResponse",
    "UserCreate",
    "UserResponse",
    "UserUpdate",
    "AccountCreate",
    "AccountResponse",
    "AccountUpdate",
    "MeterCreate",
    "MeterResponse",
    "MeterUpdate",
    "ReadingCreate",
    "ReadingResponse",
    "ReadingUpdate",
    "BillCreate",
    "BillResponse",
    "BillUpdate",
    "PaymentCreate",
    "PaymentResponse",
    "PaymentUpdate",
    "LoginRequest",
    "TokenResponse",
    "ChangePasswordRequest",
    "AuthMessageResponse",
]