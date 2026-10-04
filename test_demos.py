from backend.services.ml_service import ml_service
import json

with open('backend/demo_data.json', 'r') as f:
    data = json.load(f)

print("--- FRAUD DEMO EXAMPLES ---")
for i, txn in enumerate(data['fraud']):
    res = ml_service.predict(txn)
    print(f"Fraud Example {i}: prob={res['fraud_probability']}%, risk={res['risk_level']}")

print("\n--- LEGITIMATE DEMO EXAMPLES ---")
for i, txn in enumerate(data['legitimate']):
    res = ml_service.predict(txn)
    print(f"Legit Example {i}: prob={res['fraud_probability']}%, risk={res['risk_level']}")
