from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import and_
from sqlalchemy.orm import Session
from typing import List
from app.models import Category, SubCategory
from app.db import get_db
from app.schemas import CategoryResponse, SubCategoryResponse

router = APIRouter()


@router.get("/list", response_model=List[CategoryResponse])
def list_categories(db: Session = Depends(get_db)):
    return db.query(Category).all()


@router.get("/get/{category_id}", response_model=CategoryResponse)
def get_category(category_id: int, db: Session = Depends(get_db)):
    category = db.query(Category).filter(and_(Category.id == category_id)).first()
    if not category:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Category not found")
    return category


@router.get("/get/{category_id}/subcategories", response_model=List[SubCategoryResponse])
def list_subcategories(category_id: int, db: Session = Depends(get_db)):
    return db.query(SubCategory).filter(and_(SubCategory.category_id == category_id)).all()
