from datetime import datetime

from sqlalchemy import and_
from sqlalchemy.orm import Session

from app.db.session import get_background_task_db
from app.models import User

from app.core import logger


def update_last_login(user_id: int):
    db: Session = get_background_task_db()
    try:
        db.query(User).filter(and_(User.id == user_id)).update({"last_login": datetime.now()})
        db.commit()
    except Exception as e:
        db.rollback()
        logger.error(e)
    finally:
        db.close()


def update_user_refresh_token(user_id: int, new_token: str | None):
    db: Session = get_background_task_db()
    try:
        db.query(User).filter(and_(User.id == user_id)).update({"refresh_token": new_token})
        db.commit()
    except Exception as e:
        db.rollback()
        logger.error(e)
    finally:
        db.close()
