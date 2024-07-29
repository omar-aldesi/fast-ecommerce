from app.db import Base
from sqlalchemy import Column, Integer, String, Float, ForeignKey, Boolean, JSON
from sqlalchemy.orm import relationship
from datetime import datetime


class ShippingAddress(Base):
    __tablename__ = "shipping_addresses"
    id = Column(Integer, primary_key=True, index=True)

    orders = relationship("Order", back_populates="shipping_address", uselist=False)

    address = Column(String)

    longitude = Column(Float)
    latitude = Column(Float)


class ShippingOrder(Base):
    __tablename__ = "shipping_orders"
    id = Column(Integer, primary_key=True, index=True)

    fee = Column(Float)
    status = Column(String)

    created_at = Column(String, default=datetime.now)

    shipping_client = Column(String)
    shipping_client_data = Column(JSON)

    order_id = Column(Integer, ForeignKey("orders.id"))
    order = relationship("Order", back_populates="shipping_order")

    user_id = Column(Integer, ForeignKey("users.id"))
    user = relationship("User", back_populates="shipping_orders")
