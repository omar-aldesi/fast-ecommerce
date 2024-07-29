from sqlalchemy import and_
from sqlalchemy.orm import Session
from typing import Type

from app.models import Order
from app.core import logger

from fastapi import HTTPException
from sqlalchemy.exc import SQLAlchemyError
from app.models import User


def get_order_by_id(db: Session, order_id: int, user: User) -> Order | None:
    order = db.query(Order).get(order_id)
    if order.user_id != user.id:
        raise HTTPException(status_code=403, detail="You are not authorized to view this order")
    if not order:
        raise HTTPException(status_code=404, detail="Order not found")
    return order


def get_user_orders(db: Session, user_id: int) -> list[Type[Order]]:
    try:
        return db.query(Order).filter(and_(Order.user_id == user_id)).all()
    except SQLAlchemyError as e:
        logger.error(str(e))
        raise HTTPException(status_code=500, detail=str(e))
    except Exception as e:
        logger.error(str(e))
        raise HTTPException(status_code=500, detail=str(e))


def get_branch_orders(db: Session, branch_id: int) -> list[Type[Order]]:
    try:
        return db.query(Order).filter(and_(Order.branch_id == branch_id)).all()
    except SQLAlchemyError as e:
        logger.error(str(e))
        raise HTTPException(status_code=500, detail=str(e))
    except Exception as e:
        logger.error(str(e))
        raise HTTPException(status_code=500, detail=str(e))
