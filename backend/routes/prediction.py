from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from backend.schemas import TransactionInput, PredictionResponse
from backend.database import get_db
from backend.models import Transaction
from backend.services.ml_service import ml_service

router = APIRouter(prefix="/predict", tags=["Prediction"])

@router.post("/", response_model=PredictionResponse)
def predict_fraud(transaction_input: TransactionInput, db: Session = Depends(get_db)):
    try:
        # 1. Predict
        result = ml_service.predict(transaction_input.features)
        
        # 2. Extract amount for logging
        amount = transaction_input.features.get("Amount", 0.0)
        
        # 3. Save to database
        db_transaction = Transaction(
            amount=amount,
            prediction=result["prediction"],
            fraud_probability=result["fraud_probability"],
            risk_level=result["risk_level"]
        )
        db.add(db_transaction)
        db.commit()
        db.refresh(db_transaction)
        
        return result
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
