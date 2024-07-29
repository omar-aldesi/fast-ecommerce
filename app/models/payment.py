from app.db import Base
from sqlalchemy import Column, Integer, String, ForeignKey, Numeric
from sqlalchemy.orm import relationship


class Payment(Base):
    __tablename__ = "payments"

    id = Column(Integer, primary_key=True, index=True)

    amount = Column(Numeric(precision=10, scale=2))
    currency = Column(String)
    status = Column(String)
    gateway = Column(String)

    payment_intent_id = Column(String)
    payment_client_secret = Column(String)
    receipt_email = Column(String)

    user_id = Column(Integer, ForeignKey("users.id"))
    user = relationship("User", back_populates="payments")

    order_id = Column(Integer, ForeignKey("orders.id"))
    order = relationship("Order", back_populates="payment")
