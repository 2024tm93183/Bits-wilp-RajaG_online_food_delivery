
from fastapi import FastAPI, HTTPException, Depends
from pydantic import BaseModel
import typing as t
from .database import SessionLocal
from .models import Base, Customer, Address
from .crud import init_db
from sqlalchemy.orm import Session
import uvicorn, os

init_db()

app = FastAPI(title="customer_service")

class CustomerIn(BaseModel):
    name: str
    email: str
    phone: t.Optional[str]

class AddressIn(BaseModel):
    customer_id: int
    line1: t.Optional[str]
    area: t.Optional[str]
    city: t.Optional[str]
    pincode: t.Optional[str]

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@app.post("/v1/customers", status_code=201)
def create_customer(payload: CustomerIn, db: Session = Depends(get_db)):
    c = Customer(name=payload.name, email=payload.email, phone=payload.phone)
    db.add(c); db.commit(); db.refresh(c)
    return {"customer_id": c.customer_id, "name": c.name, "email": c.email}

@app.get("/v1/customers/{customer_id}")
def get_customer(customer_id: int, db: Session = Depends(get_db)):
    c = db.query(Customer).filter(Customer.customer_id==customer_id).first()
    if not c: raise HTTPException(status_code=404, detail="Customer not found")
    return {"customer_id": c.customer_id, "name": c.name, "email": c.email, "phone": c.phone}

@app.post("/v1/addresses", status_code=201)
def create_address(payload: AddressIn, db: Session = Depends(get_db)):
    cust = db.query(Customer).filter(Customer.customer_id==payload.customer_id).first()
    if not cust:
        raise HTTPException(status_code=400, detail="Invalid customer_id")
    a = Address(customer_id=payload.customer_id, line1=payload.line1, area=payload.area, city=payload.city, pincode=payload.pincode)
    db.add(a); db.commit(); db.refresh(a)
    return {"address_id": a.address_id, "city": a.city}

@app.get("/health")
def health():
    return {"status":"ok"}

if __name__ == '__main__':
    uvicorn.run('app.main:app', host='0.0.0.0', port=8001)
