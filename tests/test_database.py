from fastapi.testclient import TestClient
from backend.main import app
from backend.database import get_db, Base, engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy import create_engine
import pytest

# Use a separate test database
SQLALCHEMY_DATABASE_URL = "sqlite:///./test_transactions.db"
engine_test = create_engine(SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False})
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine_test)

Base.metadata.create_all(bind=engine_test)

def override_get_db():
    try:
        db = TestingSessionLocal()
        yield db
    finally:
        db.close()

app.dependency_overrides[get_db] = override_get_db
client = TestClient(app)

def test_prediction_and_db_insertion():
    # Make a prediction request
    payload = {
        "features": {
            "Amount": 100.0,
            "V1": 0.0,
            "V2": 0.0
        }
    }
    response = client.post("/predict/", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert "prediction" in data
    assert "fraud_probability" in data
    
    # Check if it was inserted into the database via transactions endpoint
    tx_response = client.get("/transactions/")
    assert tx_response.status_code == 200
    tx_data = tx_response.json()
    assert len(tx_data) >= 1
    assert tx_data[0]["amount"] == 100.0
