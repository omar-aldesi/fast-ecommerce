from pydantic import BaseModel
from typing import Optional


class ReviewBase(BaseModel):
    product_id: int
    rating: int
    comment: str


class ReviewCreate(ReviewBase):
    pass


class ReviewResponse(ReviewBase):
    id: int

    class Config:
        from_attributes = True


class ReviewUpdate(BaseModel):
    review_id: int
    rating: Optional[int] = None
    comment: Optional[str] = None
