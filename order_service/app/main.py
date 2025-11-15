
from fastapi import FastAPI, HTTPException, Depends, Header
from pydantic import BaseModel
import typing as t, requests, json, os
from .database import SessionLocal
from .models import Base, Order, OrderItem, OutboxEvent
from .crud import init_db
from sqlalchemy.orm import Session
import uvicorn

init_db()

app = FastAPI(title="order_service")

TAX_RATE = 0.05
DELIVERY_FEE = 30.0

class OrderItemIn(BaseModel):
    item_id: int
    quantity: int

class OrderIn(BaseModel):
    customer_id: int
    restaurant_id: int
    address_id: int
    items: t.List[OrderItemIn]
    payment_method: str

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

def validate_order(restaurant_id, items):
    # attempt to call restaurant service for availability
    try:
        r = requests.get("http://restaurant_service:8002/v1/menu_items", timeout=5)
        if r.status_code!=200:
            return False
    except:
        return False
    return True

@app.post("/v1/orders", status_code=201)
def create_order(payload: OrderIn, idempotency_key: str = Header(None), db: Session = Depends(get_db)):
    if len(payload.items) > 20:
        raise HTTPException(status_code=400, detail="Max 20 items per order")
    for it in payload.items:
        if it.quantity > 5:
            raise HTTPException(status_code=400, detail="Max 5 per line item")
    if not validate_order(payload.restaurant_id, payload.items):
        raise HTTPException(status_code=400, detail="Restaurant validation failed")
    subtotal = 0.0
    # naive price fetch: call menu_items endpoint and match by item_id
    try:
        r = requests.get(f"http://restaurant_service:8002/v1/menu_items?restaurant_id={payload.restaurant_id}", timeout=5)
        menu = r.json().get("items", [])
    except:
        menu = []
    for it in payload.items:
        price = 100.0
        for m in menu:
            if m.get("item_id")==it.item_id:
                price = m.get("price", price)
        subtotal += price * it.quantity
    total = round(subtotal * (1+TAX_RATE) + DELIVERY_FEE,2)
    o = Order(customer_id=payload.customer_id, restaurant_id=payload.restaurant_id, address_id=payload.address_id, order_total=total, payment_status="PENDING")
    db.add(o); db.commit(); db.refresh(o)
    for it in payload.items:
        oi = OrderItem(order_id=o.order_id, item_id=it.item_id, quantity=it.quantity, price=100.0)
        db.add(oi)
    db.commit()
    # call payment service
    pay_payload = {"order_id": o.order_id, "amount": float(o.order_total), "method": payload.payment_method}
    headers = {}
    if idempotency_key:
        headers["Idempotency-Key"] = idempotency_key
    try:
        resp = requests.post("http://payment_service:8004/v1/payments/charge", json=pay_payload, headers=headers, timeout=10)
    except Exception as e:
        raise HTTPException(status_code=502, detail="Payment service error")
    if resp.status_code!=200:
        raise HTTPException(status_code=400, detail="Payment failed")
    pay_res = resp.json()
    o.payment_status = pay_res.get("status","SUCCESS")
    if o.payment_status=="SUCCESS":
        o.order_status = "CONFIRMED"
        ev = OutboxEvent(aggregate_id=str(o.order_id), event_type="OrderConfirmed", payload=json.dumps({"order_id": o.order_id}), published=False)
        db.add(ev); db.commit()
        # notify
        try:
            requests.post("http://notification_service:8006/v1/notify", json={"event":"OrderConfirmed","order_id":o.order_id}, timeout=3)
        except:
            pass
        # call delivery
        try:
            requests.post("http://delivery_service:8005/v1/deliveries/assign", json={"order_id":o.order_id,"restaurant_id":o.restaurant_id,"address_id":o.address_id}, timeout=3)
        except:
            pass
    db.commit()
    return {"order_id": o.order_id, "order_total": float(o.order_total), "status": o.order_status}

@app.get("/v1/orders/{order_id}")
def get_order(order_id: int, db: Session = Depends(get_db)):
    o = db.query(Order).filter(Order.order_id==order_id).first()
    if not o:
        raise HTTPException(status_code=404, detail="Order not found")
    items = db.query(OrderItem).filter(OrderItem.order_id==order_id).all()
    return {"order_id": o.order_id, "status": o.order_status, "payment_status": o.payment_status, "items":[{"item_id":it.item_id,"qty":it.quantity} for it in items]}

@app.get("/health")
def health():
    return {"status":"ok"}

if __name__ == '__main__':
    uvicorn.run('app.main:app', host='0.0.0.0', port=8003)
