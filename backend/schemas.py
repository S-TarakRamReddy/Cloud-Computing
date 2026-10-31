from pydantic import BaseModel, Field
from datetime import datetime
from typing import Dict, Any, List, Optional

class TransactionInput(BaseModel):
    # Depending on the dataset, we have V1-V28, Time, Amount
    features: Dict[str, float] = Field(..., description="Dictionary of transaction features including Amount and V1-V28")

class SensitivityInput(BaseModel):
    features: Dict[str, float]
    feature: str
    low: float
    high: float
    points: int = Field(60, ge=5, le=200)

class Factor(BaseModel):
    feature: str
    value: float
    contribution: float
    direction: str

class PredictionResponse(BaseModel):
    prediction: str
    fraud_probability: float
    risk_level: str
    decision_threshold: float
    model: str
    feature_count: int
    top_factors: List[Factor] = []

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
