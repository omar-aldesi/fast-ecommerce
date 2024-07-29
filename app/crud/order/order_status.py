from fastapi import HTTPException, status
from sqlalchemy import and_
from sqlalchemy.orm import Session
from app.models import User, Order
from sqlalchemy.exc import SQLAlchemyError
from app.core import logger


def order_cancellation(db: Session, order_id: int, user: User):
    order = db.query(Order).filter(and_(Order.id == order_id)).first()
    if not order:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Order not found")
    if order.user_id != user.id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="You are not authorized to cancel this order")
    if order.status == "cancelled":
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Order is already cancelled")
    try:
        order.status = "cancelled"
        db.commit()
        return {"message": "Order cancelled successfully"}
    except SQLAlchemyError as e:
        db.rollback()
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Database error occurred")


def updating_order_status(db: Session, order_id: int, new_order_status: str, user: User):
    order = db.query(Order).filter(and_(Order.id == order_id)).first()
    if not order:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Order not found")
    if order.user_id != user.id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="You are not authorized to update this order")
    if order.status == new_order_status:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Order status is already updated")
    try:
        order.status = new_order_status
        db.commit()
        return {"message": f"Order status updated successfully to {new_order_status}"}
    except SQLAlchemyError as e:
        logger.error(e)
        db.rollback()
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Database error occurred")
