from datetime import datetime, timezone
from typing import List, Type
from fastapi import HTTPException, status
from sqlalchemy import and_
from sqlalchemy.orm import Session

from app.models import Product
from app.models.product import ProductReview
from app.schemas.review import ReviewUpdate
from app.core import logger


def list_all_products(db: Session) -> list[Type[Product]]:
    products = db.query(Product).filter(Product.is_active == True)
    return products


def get_product_by_id(db: Session, product_id: int) -> Product:
    product = db.query(Product).get(product_id)
    if not product:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Product not found")
    return product


def filter_products_by_branch(db: Session, branch_id: int = None, branch_name: str = None) -> List[Product] | []:
    products = db.query(Product)
    if branch_id:
        return products.filter(and_(Product.branch_id == branch_id))
    if branch_name:
        return products.filter(Product.branch.has(name=branch_name.lower()))
    raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid request")


def filter_products_by_category(db: Session, category_id: int = None, category_name: str = None) -> List[Product] | []:
    products = db.query(Product)
    if category_id:
        return products.filter(and_(Product.category_id == category_id))
    if category_name:
        return products.filter(Product.category.has(name=category_name.lower()))
    raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid request")


def filter_product_by_subcategory(db: Session, subcategory_id: int = None, subcategory_name: str = None) -> List[
                                                                                                                Product] | []:
    products = db.query(Product)
    if subcategory_id:
        return products.filter(and_(Product.subcategory_id == subcategory_id))
    if subcategory_name:
        return products.filter(Product.subcategory.has(name=subcategory_name.lower()))
    raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid request")


def create_product_review(db: Session, user_id: int, product_id: int, rating: int, comment: str) -> ProductReview:
    product = get_product_by_id(db, product_id)
    if not product:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Product not found")
    review = ProductReview(product_id=product_id, user_id=user_id, rating=rating, comment=comment)
    db.add(review)
    db.commit()
    db.refresh(review)
    return review


def update_product_review(db: Session, fields: ReviewUpdate) -> dict:
    try:
        update_data = fields.model_dump(exclude_unset=True)
        review = db.query(ProductReview).get(fields.review_id)
        if not review:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Review not found")
        if not update_data:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,
                                detail="No valid fields to update")
        if fields.comment:
            review.comment = fields.comment
        if fields.rating:
            review.rating = fields.rating
        review.updated_at = datetime.now(timezone.utc)
        db.add(review)
        db.commit()
        db.refresh(review)
        return {"message": "Review updated successfully"}

    except HTTPException as e:
        raise e
    except Exception as e:
        logger.error("Error updating user: %s", str(e))
        raise HTTPException(status_code=500, detail="Internal Server Error")
