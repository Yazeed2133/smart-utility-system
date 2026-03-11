from sqlalchemy import Column, Integer, Float, String, DateTime, ForeignKey
from datetime import datetime
from app.database import Base


class Bill(Base):
    __tablename__ = "bills"

    id = Column(Integer, primary_key=True, index=True)
    billing_month = Column(String, nullable=False)
    electricity_amount = Column(Float, default=0.0)
    water_amount = Column(Float, default=0.0)
    total_amount = Column(Float, nullable=False)
    status = Column(String, default="unpaid")
    due_date = Column(DateTime, default=datetime.utcnow)
    created_at = Column(DateTime, default=datetime.utcnow)
    account_id = Column(Integer, ForeignKey("accounts.id"), nullable=False)