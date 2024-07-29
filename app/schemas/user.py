import uuid

from pydantic import BaseModel, EmailStr, field_validator
from typing import Optional, List
from datetime import datetime
from .notification import NotificationResponse


class UserBase(BaseModel):
    email: EmailStr
    first_name: str
    last_name: str


class UserCreate(UserBase):
    password: str


class UserResponse(UserBase):
    id: int

    class Config:
        from_attributes = True


class UserLogin(BaseModel):
    email: str
    password: str


class UserChangePassword(BaseModel):
    old_password: str
    new_password: str


class UserPasswordReset(BaseModel):
    token: uuid.UUID
    new_password: str


class UserUpdate(BaseModel):
    email: Optional[EmailStr] = None
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    phone_number: Optional[str] = None

    @field_validator('first_name', 'last_name', 'email', 'phone_number')
    def not_empty(cls, v):
        if v == '':
            raise ValueError('Must not be empty')
        return v


class UserProfile(UserBase):
    id: int
    is_verified: bool
    is_active: bool
    phone_number: Optional[str] = None
    last_login: Optional[datetime] = None
    notifications: Optional[List[NotificationResponse]] = None

    class Config:
        from_attributes = True
