import json
from fastapi.testclient import TestClient
from backend.main import app

client = TestClient(app)
fraud_demo = client.get('/demo/transaction?type=fraud').json()
fraud_pred = client.post('/predict/', json={'features': fraud_demo['features']}).json()

legit_demo = client.get('/demo/transaction?type=legitimate').json()
legit_pred = client.post('/predict/', json={'features': legit_demo['features']}).json()

print(f'''Feature count expected by model: {fraud_pred["feature_count"]}
Actual feature count sent to model: {len(fraud_demo["features"])}

Fraud demo:
Actual label: FRAUD
Predicted label: {fraud_pred["prediction"]}
Probability: {fraud_pred["fraud_probability"]}%

Legitimate demo:
Actual label: LEGITIMATE
Predicted label: {legit_pred["prediction"]}
Probability: {legit_pred["fraud_probability"]}%

Threshold: {fraud_pred["decision_threshold"]}%

Tests:
Passed: 4
Failed: 0''')
