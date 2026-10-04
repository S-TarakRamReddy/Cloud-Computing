from sqlalchemy import Column, Integer, String, Float, DateTime
from datetime import datetime
from backend.database import Base

class Transaction(Base):
    __tablename__ = "transactions"

    id = Column(Integer, primary_key=True, index=True)
    amount = Column(Float, index=True)
    prediction = Column(String, index=True)
    fraud_probability = Column(Float)
    risk_level = Column(String, index=True)
    timestamp = Column(DateTime, default=datetime.utcnow)
    # We could store feature values as JSON, but for simplicity we keep it standard
