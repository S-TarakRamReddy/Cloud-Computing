import json
import os

from fastapi.testclient import TestClient

from backend.main import app
from backend.services.ml_service import ml_service

client = TestClient(app)

with open(os.path.join(os.path.dirname(__file__), "..", "backend", "demo_data.json")) as f:
    DEMO = json.load(f)


def test_health_check():
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json()["status"] == "healthy"


def test_prediction_endpoint():
    response = client.post("/predict/", json={"features": DEMO["legitimate"][0]})
    assert response.status_code == 200
    data = response.json()
    assert data["prediction"] == "LEGITIMATE"
    assert 0.0 <= data["fraud_probability"] <= 1.0
    assert data["feature_count"] == 29
    assert data["risk_level"] == "LOW"


def test_fraud_sample_is_flagged():
    response = client.post("/predict/", json={"features": DEMO["fraud"][0]})
    assert response.status_code == 200
    data = response.json()
    assert (data["fraud_probability"] >= data["decision_threshold"]) == (data["prediction"] == "FRAUD")


def test_prediction_rejects_missing_features():
    response = client.post("/predict/", json={"features": {"Amount": 100.0, "V1": 0.0}})
    assert response.status_code == 422


def test_prediction_rejects_unknown_features():
    features = dict(DEMO["legitimate"][0], Bogus=1.0)
    response = client.post("/predict/", json={"features": features})
    assert response.status_code == 422


def test_risk_tiers_follow_threshold():
    thr = ml_service.threshold

    class Stub:
        def __init__(self, p): self.p = p
        def predict_proba(self, _): return [[1 - self.p, self.p]]

    original = ml_service.model
    try:
        sample = DEMO["legitimate"][0]
        for p, expected in [(thr * 0.9, "LOW"), (thr * 1.2, "MEDIUM"), (thr * 2.0, "HIGH")]:
            ml_service.model = Stub(p)
            assert ml_service.predict(sample)["risk_level"] == expected
    finally:
        ml_service.model = original


def test_statistics():
    response = client.get("/statistics/")
    assert response.status_code == 200
    assert "total_transactions" in response.json()


def test_unknown_transaction_returns_404():
    assert client.get("/transactions/999999999").status_code == 404


def test_pagination_limit_is_bounded():
    assert client.get("/transactions/?limit=100000").status_code == 422


def test_demo_invalid_type_rejected():
    assert client.get("/demo/transaction?type=bogus").status_code == 422
