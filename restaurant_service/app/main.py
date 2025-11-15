
from fastapi import FastAPI, HTTPException, Depends, Query
from pydantic import BaseModel
import typing as t
from .database import SessionLocal
from .models import Base, Restaurant, MenuItem
from .crud import init_db
from sqlalchemy.orm import Session
import uvicorn, os

init_db()
app = FastAPI(title="restaurant_service")

class RestaurantIn(BaseModel):
    name: str
    cuisine: t.Optional[str]
    city: t.Optional[str]
    rating: t.Optional[float]
    is_open: t.Optional[bool] = True

class MenuItemIn(BaseModel):
    restaurant_id: int
    name: str
    category: t.Optional[str]
    price: float
    is_available: t.Optional[bool] = True

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@app.post("/v1/restaurants", status_code=201)
def create_restaurant(payload: RestaurantIn, db: Session = Depends(get_db)):
    r = Restaurant(name=payload.name, cuisine=payload.cuisine, city=payload.city, rating=payload.rating, is_open=payload.is_open)
    db.add(r); db.commit(); db.refresh(r)
    return {"restaurant_id": r.restaurant_id, "name": r.name}

@app.post("/v1/menu_items", status_code=201)
def create_menu_item(payload: MenuItemIn, db: Session = Depends(get_db)):
    rest = db.query(Restaurant).filter(Restaurant.restaurant_id==payload.restaurant_id).first()
    if not rest:
        raise HTTPException(status_code=400, detail="Invalid restaurant_id")
    m = MenuItem(restaurant_id=payload.restaurant_id, name=payload.name, category=payload.category, price=payload.price, is_available=payload.is_available)
    db.add(m); db.commit(); db.refresh(m)
    return {"item_id": m.item_id, "name": m.name, "price": float(m.price)}

@app.get("/v1/menu_items")
def list_menu_items(restaurant_id: t.Optional[int]=None, page:int=1, size:int=20, db: Session = Depends(get_db)):
    q = db.query(MenuItem)
    if restaurant_id:
        q = q.filter(MenuItem.restaurant_id==restaurant_id)
    total = q.count()
    items = q.offset((page-1)*size).limit(size).all()
    return {"total": total, "items":[{"item_id": it.item_id, "name": it.name, "price": float(it.price)} for it in items]}

@app.get("/health")
def health():
    return {"status":"ok"}

if __name__ == '__main__':
    uvicorn.run('app.main:app', host='0.0.0.0', port=8002)
