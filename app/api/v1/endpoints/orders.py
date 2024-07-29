from typing import List

from fastapi import APIRouter, Depends, HTTPException, status

from app.core.deps import get_current_user
from app.db import get_db
from sqlalchemy.orm import Session

from app.models import User
from app.schemas.order import OrderCreate, OrderResponse, OrderStatusEnum, OrderUpdateStatus
from app.crud.order import create_order as order_creation, get_user_orders, get_order_by_id, order_cancellation, \
    updating_order_status
from app.core import logger

router = APIRouter()


@router.post("/create", response_model=OrderResponse)
async def create_order(request: OrderCreate, db: Session = Depends(get_db),
                       user: User = Depends(get_current_user)):
    try:
        new_order = await order_creation(db, request, user)
        db.commit()
        return new_order
    except HTTPException as e:
        logger.error(e.detail)
        db.rollback()
        raise e
    except Exception as e:
        logger.error(str(e))
        db.rollback()
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))


@router.get("/list", response_model=List[OrderResponse])
def list_orders(db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    return get_user_orders(db, user.id)


@router.get("/get/{order_id}", response_model=OrderResponse)
def get_order(order_id: int, db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    return get_order_by_id(db, order_id, user)


@router.put("/cancel/{order_id}")
def cancel_order(order_id: int, db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    return order_cancellation(db, order_id, user)


@router.put("/update_status")
def order_status(request: OrderUpdateStatus, db: Session = Depends(get_db),
                 user: User = Depends(get_current_user)):
    return updating_order_status(db, request.order_id, request.status.value, user)
