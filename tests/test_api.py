from fastapi.testclient import TestClient
from backend.main import app

client = TestClient(app)

def test_health_check():
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "healthy"}

def test_prediction_endpoint():
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
    assert "decision_threshold" in data
    assert "model" in data
    assert "feature_count" in data

def test_statistics():
    response = client.get("/statistics/")
    assert response.status_code == 200
    assert "total_transactions" in response.json()
