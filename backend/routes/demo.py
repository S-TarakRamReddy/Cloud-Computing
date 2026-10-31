from typing import Literal
from fastapi import APIRouter, HTTPException
import json
import os
import random

router = APIRouter(prefix="/demo", tags=["Demo"])

# Load demo data in memory
base_dir = os.path.dirname(os.path.dirname(__file__))
demo_file = os.path.join(base_dir, "demo_data.json")

demo_data = {"fraud": [], "legitimate": []}
if os.path.exists(demo_file):
    with open(demo_file, "r") as f:
        demo_data = json.load(f)

from backend.services.ml_service import ml_service

@router.get("/transaction")
def get_demo_transaction(
    type: Literal["fraud", "legitimate", "random"] = "random",
    honest: bool = False,
):
    """Return a labelled dataset transaction.

    By default fraud/legitimate picks only samples the model gets right (a clean demo).
    With honest=true any labelled sample can be returned, including ones the model misses.
    """
    if type == "random":
        actual_type = random.choice(["fraud", "legitimate"])
        transactions = demo_data.get(actual_type, [])
        if not transactions:
            raise HTTPException(status_code=404, detail="No demo data available")
        transaction = random.choice(transactions)
        return {
            "type": actual_type.upper(),
            "features": transaction
        }
        
    transactions = demo_data.get(type, [])
    if not transactions:
        raise HTTPException(status_code=404, detail="No demo data available")
        
    if honest:
        return {"type": type.upper(), "features": random.choice(transactions)}

    # We want a random one that matches the expected prediction
    shuffled_transactions = random.sample(transactions, len(transactions))
    for transaction in shuffled_transactions:
        res = ml_service.predict(transaction)
        if type == "fraud" and res["prediction"] == "FRAUD" and res["risk_level"] == "HIGH":
            return {"type": "FRAUD", "features": transaction}
        if type == "legitimate" and res["prediction"] == "LEGITIMATE":
            return {"type": "LEGITIMATE", "features": transaction}
            
    # Fallback if none match
    transaction = random.choice(transactions)
    return {
        "type": type.upper(),
        "features": transaction
    }
