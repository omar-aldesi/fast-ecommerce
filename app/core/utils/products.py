from sqlalchemy.orm import Session

from app.models import Product
from datetime import datetime, timedelta
from sqlalchemy import update, and_


def update_product_daily_stock(db: Session, product: Product):
    product.stock = product.stock_daily
    product.last_daily_stock_update = datetime.now().date()
    db.commit()


def update_product_stocks(db: Session, product: Product, quantity):
    if product.stock_type.upper() == 'FIXED':
        stmt = update(Product).where(and_(Product.id == product.id)).values(stock=Product.stock - quantity)
    elif product.stock_type.upper() == 'DAILY':
        stmt = update(Product).where(and_(Product.id == product.id)).values(
            available_daily_stock=Product.stock - quantity)
    elif product.stock_type.upper() == 'UNLIMITED':
        # No need to update stock for unlimited products
        return
    else:
        raise ValueError(f"Unknown stock type: {product.stock_type}")

    db.execute(stmt)
    db.commit()
    db.refresh(product)


def check_product_stocks(db: Session, product: Product, quantity: int):
    if product.stock_type.upper() == 'UNLIMITED':
        return True
    elif product.stock_type.upper() == 'DAILY':
        now = datetime.now().date()
        if now >= (product.last_daily_stock_update + timedelta(days=1)):
            update_product_daily_stock(db, product)
        if product.stock < quantity:
            return False
    elif product.stock_type.upper() == 'FIXED':
        if product.stock < quantity:
            return False
    else:
        raise ValueError(f"Unknown stock type: {product.stock_type}")

    update_product_stocks(db, product, quantity)
    return True
