from app.models.user import User
from sqlalchemy.orm import Session
from sqlalchemy import and_


def get_user_by_email(db: Session, email: str):
    return db.query(User).filter(User.email.like(email)).first()


def get_user_by_id(db: Session, user_id: int):
    return db.query(User).filter(and_(User.id == user_id)).first()
