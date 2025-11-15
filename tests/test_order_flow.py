import requests, uuid
def test_order_flow_local():
    c = requests.post('http://localhost:8001/v1/customers', json={'name':'Test','email':'t@example.com'}).json()
    r = requests.post('http://localhost:8002/v1/restaurants', json={'name':'Demo','city':'Mumbai'}).json()
    mi = requests.post('http://localhost:8002/v1/menu_items', json={'restaurant_id': r['restaurant_id'], 'name':'Sample','price':100.0}).json()
    key = str(uuid.uuid4())
    order_payload = {'customer_id': c['customer_id'], 'restaurant_id': r['restaurant_id'], 'address_id': 1, 'items': [{'item_id': mi['item_id'], 'quantity':1}], 'payment_method':'card'}
    resp = requests.post('http://localhost:8003/v1/orders', json=order_payload, headers={'Idempotency-Key': key})
    assert resp.status_code == 201
    data = resp.json()
    assert 'order_id' in data
