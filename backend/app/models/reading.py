from sqlalchemy import Column, Integer, Float, DateTime, ForeignKey
from datetime import datetime
from app.database import Base


class Reading(Base):
    __tablename__ = "readings"

    id = Column(Integer, primary_key=True, index=True)
    reading_value = Column(Float, nullable=False)
    reading_date = Column(DateTime, default=datetime.utcnow)
    meter_id = Column(Integer, ForeignKey("meters.id"), nullable=False)