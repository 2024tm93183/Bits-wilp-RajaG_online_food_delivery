
from fastapi import FastAPI, HTTPException, Depends
from pydantic import BaseModel
import typing as t
from .database import SessionLocal
from .models import Base, Driver, Delivery
from .crud import init_db
from sqlalchemy.orm import Session
import uvicorn, datetime

init_db()
app = FastAPI(title="delivery_service")

class AssignIn(BaseModel):
    order_id: int
    restaurant_id: int
    address_id: int

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@app.post("/v1/deliveries/assign")
def assign_delivery(payload: AssignIn, db: Session = Depends(get_db)):
    d = db.query(Driver).filter(Driver.is_active==True).first()
    if not d:
        raise HTTPException(status_code=400, detail="No driver available")
    delivery = Delivery(order_id=payload.order_id, driver_id=d.driver_id, status="ASSIGNED", assigned_at=datetime.datetime.utcnow())
    db.add(delivery); db.commit(); db.refresh(delivery)
    return {"delivery_id": delivery.delivery_id, "driver_id": d.driver_id, "status": delivery.status}

@app.get("/health")
def health():
    return {"status":"ok"}

if __name__ == '__main__':
    uvicorn.run('app.main:app', host='0.0.0.0', port=8005)
