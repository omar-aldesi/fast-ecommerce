from pydantic import BaseModel, Json
from typing import Optional, List, Any
from datetime import datetime
from .review import ReviewResponse


class AddonSchema(BaseModel):
    id: int


class AddonResponseSchema(BaseModel):
    id: int
    title: str
    price: float
    tax: float

    class Config:
        from_attributes = True


class VariationOptionSchema(BaseModel):
    id: int


class VariationOptionResponseSchema(BaseModel):
    id: int
    name: str
    price: float

    class Config:
        from_attributes = True


class ProductVariationsSchema(BaseModel):
    id: int
    options: Optional[List[VariationOptionSchema]] = []


class ProductVariationsResponseSchema(BaseModel):
    id: int
    title: str
    type: str
    min_selections: int
    max_selections: int
    required: bool
    options: Optional[List[VariationOptionResponseSchema]] = []


class ProductBase(BaseModel):
    name: str
    price: float
    description: str
    image: str
    stock: int
    created_at: datetime
    updated_at: datetime | None = None
    tags: Json[Any]
    discount_type: str | None = None
    discount_value: str | None = None
    total_sales: int
    category_id: int
    subcategory_id: int
    branch_id: int


class ProductsListResponse(ProductBase):
    id: int

    class Config:
        from_attributes = True


class ProductResponse(ProductBase):
    id: int
    addons: Optional[List[AddonResponseSchema]] = []
    variations: Optional[List[ProductVariationsResponseSchema]] = []
    reviews: Optional[List[ReviewResponse]] = []

    class Config:
        from_attributes = True
