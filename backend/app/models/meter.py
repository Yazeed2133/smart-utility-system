from sqlalchemy import Column, Integer, String, ForeignKey
from app.database import Base


class Meter(Base):
    __tablename__ = "meters"

    id = Column(Integer, primary_key=True, index=True)
    meter_number = Column(String, unique=True, nullable=False, index=True)
    meter_type = Column(String, nullable=False)   # electricity or water
    status = Column(String, default="active")
    account_id = Column(Integer, ForeignKey("accounts.id"), nullable=False)