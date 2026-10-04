from pydantic import BaseModel, Field
from datetime import datetime
from typing import Dict, Any, Optional

class TransactionInput(BaseModel):
    # Depending on the dataset, we have V1-V28, Time, Amount
    features: Dict[str, float] = Field(..., description="Dictionary of transaction features including Amount and V1-V28")

class PredictionResponse(BaseModel):
    prediction: str
    fraud_probability: float
    risk_level: str
    decision_threshold: float
    model: str
    feature_count: int

class TransactionResponse(BaseModel):
    id: int
    amount: float
    prediction: str
    fraud_probability: float
    risk_level: str
    timestamp: datetime

    class Config:
        from_attributes = True

class StatisticsResponse(BaseModel):
    total_transactions: int
    fraudulent_transactions: int
    legitimate_transactions: int
    fraud_percentage: float
