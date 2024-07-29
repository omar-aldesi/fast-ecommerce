from typing import List, Optional

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.core.deps import get_current_user
from app.models import User
from app.schemas.product import ProductsListResponse, ProductResponse
from app.schemas.review import ReviewCreate, ReviewResponse, ReviewUpdate
from app.crud.products import list_all_products, get_product_by_id, filter_products_by_branch, \
    filter_products_by_category, filter_product_by_subcategory, create_product_review, update_product_review
from app.db import get_db

router = APIRouter()


@router.get("/list", response_model=List[ProductsListResponse])
def list_products(db: Session = Depends(get_db)):
    return list_all_products(db)


@router.get("/get/{product_id}", response_model=ProductResponse)
def get_product(product_id: int, db: Session = Depends(get_db)):
    return get_product_by_id(db, product_id)


@router.get("/branch/", response_model=List[ProductsListResponse])
def get_products_by_branch(branch_id: Optional[int] = None, branch_name: Optional[str] = None,
                           db: Session = Depends(get_db)):
    return filter_products_by_branch(db, branch_id, branch_name)


@router.get("/category/", response_model=List[ProductsListResponse])
def get_products_by_category(category_id: Optional[int] = None, category_name: Optional[str] = None,
                             db: Session = Depends(get_db)):
    return filter_products_by_category(db, category_id, category_name)


@router.get("/subcategory/", response_model=List[ProductsListResponse])
def get_products_by_category(subcategory_id: Optional[int] = None, subcategory_name: Optional[str] = None,
                             db: Session = Depends(get_db)):
    return filter_product_by_subcategory(db, subcategory_id, subcategory_name)


@router.post("/create-review", response_model=ReviewResponse, status_code=status.HTTP_201_CREATED)
def review_product(request: ReviewCreate, db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    return create_product_review(db, user.id, **request.model_dump())


@router.put("/update-review")
def update_review(request: ReviewUpdate, db: Session = Depends(get_db)):
    return update_product_review(db, request)
