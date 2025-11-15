from sqlalchemy import Column, Integer, String, Boolean, Numeric, DateTime, ForeignKey, Text
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.sql import func

Base = declarative_base()


class Driver(Base):
    __tablename__ = "drivers"
    driver_id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String)
    phone = Column(String)
    vehicle_type = Column(String)
    is_active = Column(Boolean, default=True)

class Delivery(Base):
    __tablename__ = "deliveries"
    delivery_id = Column(Integer, primary_key=True, autoincrement=True)
    order_id = Column(Integer)
    driver_id = Column(Integer)
    status = Column(String, default="ASSIGNED")
    assigned_at = Column(DateTime(timezone=True))
    picked_at = Column(DateTime(timezone=True))
    delivered_at = Column(DateTime(timezone=True))
