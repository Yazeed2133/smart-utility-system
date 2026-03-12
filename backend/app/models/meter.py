from sqlalchemy import Column, Integer, String, DateTime, ForeignKey
from datetime import datetime

from app.database import Base


class Meter(Base):
    __tablename__ = "meters"

    id = Column(Integer, primary_key=True, index=True)
    account_id = Column(Integer, ForeignKey("accounts.id"), nullable=False)
    meter_number = Column(String, unique=True, index=True, nullable=False)
    meter_type = Column(String, nullable=False)
    location = Column(String, nullable=False)
    installed_at = Column(DateTime, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)