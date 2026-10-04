import httpx
import sys

BASE_URL = "http://localhost:8000"

def run_tests():
    print("1. Testing /health")
    resp = httpx.get(f"{BASE_URL}/health")
    assert resp.status_code == 200
    print("Health OK:", resp.json())

    print("\n2. Testing /model-info")
    resp = httpx.get(f"{BASE_URL}/model-info")
    assert resp.status_code == 200
    print("Model Info OK:", resp.json())

    print("\n3. Testing /demo/transaction?type=legitimate")
    resp = httpx.get(f"{BASE_URL}/demo/transaction?type=legitimate")
    assert resp.status_code == 200
    legit_txn = resp.json()
    print("Legit Demo OK")

    print("\n4. Testing /demo/transaction?type=fraud")
    resp = httpx.get(f"{BASE_URL}/demo/transaction?type=fraud")
    assert resp.status_code == 200
    fraud_txn = resp.json()
    print("Fraud Demo OK")

    print("\n5. Testing /predict with Legit")
    resp = httpx.post(f"{BASE_URL}/predict/", json={"features": legit_txn['features']})
    assert resp.status_code == 200
    data = resp.json()
    print("Legit Predict OK:", data)
    assert data['prediction'] == "LEGITIMATE", "Legit demo should be predicted as LEGITIMATE"
    assert data['fraud_probability'] < data['decision_threshold'], "Probability should be below threshold"

    print("\n6. Testing /predict with Fraud")
    resp = httpx.post(f"{BASE_URL}/predict/", json={"features": fraud_txn['features']})
    assert resp.status_code == 200
    data = resp.json()
    print("Fraud Predict OK:", data)
    assert data['prediction'] == "FRAUD", "Fraud demo should always return a FRAUD prediction now"
    assert data['risk_level'] == "HIGH", "Fraud demo should always return HIGH risk now"
    
    print("\n6.1 Testing /demo/transaction?type=random")
    resp = httpx.get(f"{BASE_URL}/demo/transaction?type=random")
    assert resp.status_code == 200
    random_txn = resp.json()
    resp = httpx.post(f"{BASE_URL}/predict/", json={"features": random_txn['features']})
    assert resp.status_code == 200
    print(f"Random Demo Predict OK (Type: {random_txn['type']}):", resp.json())

    print("\n7. Testing /transactions")
    resp = httpx.get(f"{BASE_URL}/transactions/")
    assert resp.status_code == 200
    transactions = resp.json()
    print(f"Transactions retrieved: {len(transactions)} records")
    assert len(transactions) >= 2

    print("\n8. Testing /statistics")
    resp = httpx.get(f"{BASE_URL}/statistics/")
    assert resp.status_code == 200
    print("Statistics OK:", resp.json())
    
    print("\nALL API E2E TESTS PASSED SUCCESSFULLY!")

if __name__ == "__main__":
    try:
        run_tests()
    except Exception as e:
        print(f"Test failed: {e}")
        sys.exit(1)
