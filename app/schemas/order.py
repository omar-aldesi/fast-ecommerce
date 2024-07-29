from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime
from enum import Enum
from .product import AddonSchema, ProductVariationsSchema
from .shipping import ShippingAddressSchema
from decimal import Decimal
from .payment import PaymentRequestSchema


class OrderStatusEnum(Enum):
    PENDING = "pending"
    CONFIRMED = "confirmed"
    CANCELLED = "cancelled"
    DELIVERED = "delivered"


class PaymentMethodEnum(Enum):
    CASH = "cash"
    STRIPE = "stripe"
    PAYPAL = "paypal"


class OrderType(Enum):
    SHIPPING = "shipping"
    PICKUP = "pickup"


class OrderItemSchema(BaseModel):
    product_id: int
    quantity: int
    addons: Optional[List[AddonSchema]] = []
    variations: Optional[List[ProductVariationsSchema]] = []
    coupon_code: Optional[str] = None


class OrderCreate(BaseModel):
    is_scheduled: Optional[bool] = False
    scheduled_at: Optional[datetime] = None
    payment: PaymentRequestSchema
    branch_id: int
    type: OrderType
    shipping_address: ShippingAddressSchema
    products: List[OrderItemSchema] = []


class OrderItemResponse(BaseModel):
    id: int
    product_id: int
    quantity: int
    total_price: Decimal
    addons: List[AddonSchema] = []
    variations: List[ProductVariationsSchema] = []

    class Config:
        from_attributes = True


class OrderResponse(BaseModel):
    id: int
    is_scheduled: bool
    scheduled_at: Optional[datetime] = None
    branch_id: int
    type: OrderType
    shipping_address: ShippingAddressSchema
    items: List[OrderItemResponse]
    total_price: Decimal
    status: OrderStatusEnum

    class Config:
        from_attributes = True


class OrderUpdateStatus(BaseModel):
    order_id: int
    status: OrderStatusEnum
