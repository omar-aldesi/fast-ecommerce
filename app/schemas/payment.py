from pydantic import BaseModel
from decimal import Decimal
from typing import Optional


class PaymentResponse(BaseModel):
    amount: Decimal
    status: str
    currency: str
    gateway: str
    payment_intent_id: str
    receipt_email: str
    order_id: int


class PaymentRequestSchema(BaseModel):
    currency: Optional[str] = "USD"
    gateway: str
    payment_intent_id: str
    receipt_email: str
    payment_client_secret: str
