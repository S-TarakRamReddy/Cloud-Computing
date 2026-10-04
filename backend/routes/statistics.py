from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from backend.schemas import StatisticsResponse
from backend.database import get_db
from backend.models import Transaction

router = APIRouter(prefix="/statistics", tags=["Statistics"])

@router.get("/", response_model=StatisticsResponse)
def get_statistics(db: Session = Depends(get_db)):
    total = db.query(Transaction).count()
    if total == 0:
        return StatisticsResponse(
            total_transactions=0,
            fraudulent_transactions=0,
            legitimate_transactions=0,
            fraud_percentage=0.0
        )
        
    fraudulent = db.query(Transaction).filter(Transaction.prediction == "FRAUD").count()
    legitimate = total - fraudulent
    fraud_percentage = round((fraudulent / total) * 100, 2)
    
    return StatisticsResponse(
        total_transactions=total,
        fraudulent_transactions=fraudulent,
        legitimate_transactions=legitimate,
        fraud_percentage=fraud_percentage
    )
