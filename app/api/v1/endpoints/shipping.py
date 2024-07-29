from fastapi import HTTPException, APIRouter, Depends
from sqlalchemy import and_
from sqlalchemy.orm import Session
from typing import List

from app.schemas.shipping import ShippingOrderResponse
from app.core.deps import get_current_user
from app.db import get_db
from app.models import User, ShippingOrder

router = APIRouter()


@router.get("/list", response_model=List[ShippingOrderResponse])
def list_shipping_orders(db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    return db.query(ShippingOrder).filter(and_(ShippingOrder.user_id == user.id)).all()


@router.get("/get/{shipping_order_id}", response_model=ShippingOrderResponse)
def get_shipping_order(shipping_order_id: int, db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    shipping_order = db.query(ShippingOrder).filter(
        and_(ShippingOrder.id == shipping_order_id, ShippingOrder.user_id == user.id)).first()
    if not shipping_order:
        raise HTTPException(status_code=404, detail="Shipping order not found")
    return shipping_order
