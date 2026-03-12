from pydantic import BaseModel
from typing import Generic, TypeVar
from pydantic.generics import GenericModel


class MessageResponse(BaseModel):
    message: str


T = TypeVar("T")


class PaginatedResponse(GenericModel, Generic[T]):
    total: int
    items: list[T]