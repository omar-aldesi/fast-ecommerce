from app.db import Base

from sqlalchemy import Column, Integer, String, ForeignKey, Boolean, DateTime, Float, Numeric, Table
from sqlalchemy.orm import relationship
from datetime import datetime

# Association table for OrderItem and Addon
order_item_addon_association = Table(
    'order_item_addon_association',
    Base.metadata,
    Column('order_item_id', Integer, ForeignKey('order_items.id'), primary_key=True),
    Column('addon_id', Integer, ForeignKey('addons.id'), primary_key=True)
)

# Association table for OrderItem and ProductVariation
order_item_variation_association = Table(
    'order_item_variation_association',
    Base.metadata,
    Column('order_item_id', Integer, ForeignKey('order_items.id'), primary_key=True),
    Column('variation_id', Integer, ForeignKey('product_variations.id'), primary_key=True)
)


# TODO : create subtotal field and modify the funcs
class Order(Base):
    __tablename__ = "orders"

    id = Column(Integer, primary_key=True, index=True)

    total_price = Column(Numeric(10, 2))

    is_paid = Column(Boolean, default=False)

    status = Column(String, default='pending')  # pending, processing, shipped, delivered, cancelled
    created_at = Column(DateTime, default=datetime.now)
    type = Column(String)

    is_scheduled = Column(Boolean, default=False)
    schedule_time = Column(DateTime)

    shipping_order = relationship("ShippingOrder", back_populates="order")

    shipping_address_id = Column(Integer, ForeignKey("shipping_addresses.id"), nullable=True)
    shipping_address = relationship("ShippingAddress", back_populates="orders")

    items = relationship("OrderItem", back_populates="order")

    branch_id = Column(Integer, ForeignKey("branches.id"))
    branch = relationship("Branch", back_populates="orders")

    user_id = Column(Integer, ForeignKey("users.id"))
    user = relationship("User", back_populates="orders")

    payment = relationship("Payment", back_populates="order")


class OrderItem(Base):
    __tablename__ = "order_items"

    id = Column(Integer, primary_key=True, index=True)

    quantity = Column(Integer)
    total_price = Column(Float)

    product_id = Column(Integer, ForeignKey("products.id"))
    product = relationship("Product")

    order_id = Column(Integer, ForeignKey("orders.id"))
    order = relationship("Order", back_populates="items")
    # Use secondary tables for many-to-many relationships
    addons = relationship("Addon", secondary="order_item_addon_association")
    variations = relationship("ProductVariation", secondary="order_item_variation_association")
