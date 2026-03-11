from sqlalchemy import Column, Integer, String, ForeignKey
from app.database import Base


class Account(Base):
    __tablename__ = "accounts"

    id = Column(Integer, primary_key=True, index=True)
    account_number = Column(String, unique=True, nullable=False, index=True)
    address = Column(String, nullable=False)
    status = Column(String, default="active")
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)