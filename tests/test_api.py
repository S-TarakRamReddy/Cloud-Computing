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


def test_prediction_includes_explanation():
    data = client.post("/predict/", json={"features": DEMO["fraud"][1]}).json()
    factors = data["top_factors"]
    assert 1 <= len(factors) <= 6
    assert {"feature", "value", "contribution", "direction"} <= set(factors[0])
    assert factors[0]["feature"] == "V14"  # dominant signal for this model
    assert factors[0]["direction"] == "fraud"


def test_log_false_does_not_store_transaction():
    before = client.get("/statistics/").json()["total_transactions"]
    client.post("/predict/?log=false", json={"features": DEMO["legitimate"][0]})
    after = client.get("/statistics/").json()["total_transactions"]
    assert after == before


def test_model_card_available():
    card = client.get("/model-card").json()
    assert card["confusion_matrix"]["tp"] + card["confusion_matrix"]["fn"] == card["test_set"]["fraud_cases"]
    assert 0 < card["metrics"]["recall"]["ci95"][0] < card["metrics"]["recall"]["ci95"][1] <= 1
    assert abs(sum(card["feature_importance"].values()) - 1) < 0.01


def test_demo_honest_mode_returns_labelled_sample():
    data = client.get("/demo/transaction?type=fraud&honest=true").json()
    assert data["type"] == "FRAUD" and len(data["features"]) == 29


def test_sensitivity_curve():
    body = {"features": DEMO["fraud"][1], "feature": "V14", "low": -10, "high": 5, "points": 40}
    data = client.post("/predict/sensitivity", json=body).json()
    assert len(data["values"]) == len(data["probabilities"]) == 40
    assert all(0 <= p <= 1 for p in data["probabilities"])
    assert len(set(data["probabilities"])) > 1  # the answer actually moves with the feature


def test_sensitivity_rejects_unknown_feature():
    body = {"features": DEMO["fraud"][1], "feature": "Nope", "low": 0, "high": 1}
    assert client.post("/predict/sensitivity", json=body).status_code == 422


def test_borderline_samples_are_uncertain():
    for _ in range(5):
        data = client.get("/demo/transaction?type=borderline").json()
        assert data["borderline"] is True
        p = client.post("/predict/?log=false", json={"features": data["features"]}).json()["fraud_probability"]
        assert 0.1 < p < 0.95
