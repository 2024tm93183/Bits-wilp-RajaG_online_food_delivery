
from fastapi import FastAPI, HTTPException, Header, Depends
from pydantic import BaseModel
import typing as t, json, uuid
from .database import SessionLocal
from .models import Base, Payment, IdempotencyKey
from .crud import init_db
from sqlalchemy.orm import Session
import uvicorn

init_db()
app = FastAPI(title="payment_service")

class ChargeIn(BaseModel):
    order_id: int
    amount: float
    method: t.Optional[str] = "card"

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@app.post("/v1/payments/charge")
def charge(payload: ChargeIn, idempotency_key: str = Header(None), db: Session = Depends(get_db)):
    if not idempotency_key:
        raise HTTPException(status_code=400, detail="Idempotency-Key required")
    existing = db.query(IdempotencyKey).filter(IdempotencyKey.key==idempotency_key).first()
    if existing:
        try:
            return json.loads(existing.response)
        except:
            return {"status":"SUCCESS"}
    ref = str(uuid.uuid4())
    p = Payment(order_id=payload.order_id, amount=payload.amount, method=payload.method, status="SUCCESS", reference=ref)
    db.add(p); db.commit(); db.refresh(p)
    resp = {"status":"SUCCESS", "reference": ref}
    ik = IdempotencyKey(key=idempotency_key, response=json.dumps(resp))
    db.add(ik); db.commit()
    return resp

@app.get("/health")
def health():
    return {"status":"ok"}

if __name__ == '__main__':
    uvicorn.run('app.main:app', host='0.0.0.0', port=8004)
