import requests, uuid
def test_idempotency_local():
    key = str(uuid.uuid4())
    payload = { "order_id": 1, "amount": 100.0, "method": "card" }
    headers = {"Idempotency-Key": key, "Content-Type":"application/json"}
    r1 = requests.post("http://localhost:8004/v1/payments/charge", json=payload, headers=headers)
    r2 = requests.post("http://localhost:8004/v1/payments/charge", json=payload, headers=headers)
    assert r1.status_code == 200
    assert r2.status_code == 200
    assert r1.json() == r2.json()
