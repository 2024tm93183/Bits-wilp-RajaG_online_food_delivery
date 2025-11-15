from sqlalchemy import Column, Integer, String, Boolean, Numeric, DateTime, ForeignKey, Text
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.sql import func

Base = declarative_base()


class Order(Base):
    __tablename__ = "orders"
    order_id = Column(Integer, primary_key=True, autoincrement=True)
    customer_id = Column(Integer)
    restaurant_id = Column(Integer)
    address_id = Column(Integer)
    order_status = Column(String, default="CREATED")
    order_total = Column(Numeric(10,2))
    payment_status = Column(String, default="PENDING")
    created_at = Column(DateTime(timezone=True), server_default=func.now())

class OrderItem(Base):
    __tablename__ = "order_items"
    order_item_id = Column(Integer, primary_key=True, autoincrement=True)
    order_id = Column(Integer, ForeignKey("orders.order_id"))
    item_id = Column(Integer)
    quantity = Column(Integer)
    price = Column(Numeric(10,2))

class OutboxEvent(Base):
    __tablename__ = "outbox_events"
    id = Column(Integer, primary_key=True, autoincrement=True)
    aggregate_id = Column(String)
    event_type = Column(String)
    payload = Column(Text)
    published = Column(Boolean, default=False)
