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


def test_metrics_endpoint_reports_traffic_and_predictions():
    client.post("/predict/?log=false", json={"features": DEMO["fraud"][1]})
    client.post("/predict/?log=false", json={"features": DEMO["legitimate"][0]})
    text = client.get("/metrics").text
    assert "fraud_model_loaded 1.0" in text
    assert 'fraud_predictions_total{prediction="FRAUD"' in text
    assert 'fraud_predictions_total{prediction="LEGITIMATE"' in text
    assert 'fraud_api_requests_total{method="POST",path="/predict/",status="200"}' in text
    assert "fraud_api_request_seconds_bucket" in text


def test_metrics_labels_use_route_templates():
    client.get("/transactions/123456789")  # 404, but must be labelled by template
    text = client.get("/metrics").text
    assert 'path="/transactions/{tx_id}"' in text
    assert "123456789" not in text


def test_monitoring_summary_tracks_predictions():
    for sample in (DEMO["fraud"][1], DEMO["legitimate"][0], DEMO["legitimate"][1]):
        client.post("/predict/?log=false", json={"features": sample})
    d = client.get("/monitoring/summary").json()
    assert d["model_loaded"] is True
    assert len(d["timeline"]) == d["window_minutes"] == 30
    assert d["predictions"]["in_window"] >= 3
    assert set(d["predictions"]["verdicts"]) >= {"FRAUD", "LEGITIMATE"}
    assert sum(d["score_distribution"]["live_counts"]) == d["predictions"]["in_window"]
    assert len(d["score_distribution"]["baseline_share"]) == len(d["score_distribution"]["bands"])
    assert d["latency_ms"]["p95"] is not None and d["latency_ms"]["count"] >= 3
    assert 1 <= len(d["recent_predictions"]) <= 10
    assert d["recent_predictions"][0]["probability"] >= 0


def test_monitoring_summary_does_not_count_itself():
    first = client.get("/monitoring/summary").json()["totals_since_start"]["requests"]
    client.get("/monitoring/summary")
    client.get("/metrics")
    second = client.get("/monitoring/summary").json()["totals_since_start"]["requests"]
    assert first == second


def test_event_log_is_bounded():
    from backend import metrics
    assert metrics.EVENTS.maxlen == metrics.MAX_EVENTS == 5000


def test_score_histogram_is_exported():
    client.post("/predict/?log=false", json={"features": DEMO["fraud"][1]})
    assert "fraud_prediction_probability_bucket" in client.get("/metrics").text
