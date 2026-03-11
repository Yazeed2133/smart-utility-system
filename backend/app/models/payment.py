from sqlalchemy import Column, Integer, Float, String, DateTime, ForeignKey
from datetime import datetime
from app.database import Base


class Payment(Base):
    __tablename__ = "payments"

    id = Column(Integer, primary_key=True, index=True)
    amount = Column(Float, nullable=False)
    payment_method = Column(String, nullable=False)   # card, cash, kiosk, wallet
    payment_status = Column(String, default="completed")
    transaction_ref = Column(String, nullable=True)
    paid_at = Column(DateTime, default=datetime.utcnow)
    bill_id = Column(Integer, ForeignKey("bills.id"), nullable=False)