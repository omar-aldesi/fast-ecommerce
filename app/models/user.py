from sqlalchemy import Column, Integer, String, Boolean, DateTime, ForeignKey, UUID
from sqlalchemy.orm import relationship
from app.db import Base
from app.core.security import hash_password, verify_password
from datetime import datetime

import uuid


class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, index=True)
    hashed_password = Column(String)
    first_name = Column(String)
    last_name = Column(String)
    phone_number = Column(String)
    is_verified = Column(Boolean, default=False)
    is_active = Column(Boolean, default=True)
    is_superuser = Column(Boolean, default=False)
    last_login = Column(DateTime, nullable=True, default=datetime.now)
    refresh_token = Column(String, nullable=True)
    email_verification_token = relationship("EmailVerificationToken", back_populates='user')
    password_reset_token = relationship("ResetPasswordToken", back_populates='user')
    orders = relationship("Order", back_populates='user')

    notifications = relationship("Notification", back_populates='user')
    shipping_orders = relationship("ShippingOrder", back_populates='user')
    payments = relationship("Payment", back_populates='user')

    def set_password(self, password: str) -> bool:
        try:
            self.hashed_password = hash_password(password)
            return True
        except Exception as e:
            raise e

    def check_password(self, password: str) -> bool:
        if verify_password(self.hashed_password, password):
            return True
        else:
            return False


class EmailVerificationToken(Base):
    __tablename__ = 'email_verification_tokens'
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), unique=True)
    user = relationship("User", back_populates="email_verification_token")
    token = Column(UUID(as_uuid=True), default=uuid.uuid4, index=True)
    created_at = Column(DateTime(timezone=True), default=datetime.now)


class ResetPasswordToken(Base):
    __tablename__ = 'reset_password_tokens'
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), unique=True)
    user = relationship("User", back_populates="password_reset_token")
    token = Column(UUID(as_uuid=True), default=uuid.uuid4, index=True)
    created_at = Column(DateTime(timezone=True), default=datetime.now)
