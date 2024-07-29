from datetime import datetime

from pydantic import BaseModel, Json


class ShippingAddressSchema(BaseModel):
    longitude: float
    latitude: float
    address: str


class ShippingOrderResponse(BaseModel):
    id: int
    status: str
    fee: float
    created_at: datetime
    shipping_client: str
    shipping_client_data: Json
    order_id: int
