from pydantic import BaseModel
from typing import List


class SubCategoryResponse(BaseModel):
    id: int
    name: str


class CategoryResponse(BaseModel):
    id: int
    name: str
    priority: int
    banner_image: str
    image: str
    subcategories: List[SubCategoryResponse] = []
