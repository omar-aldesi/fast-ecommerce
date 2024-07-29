import os
from datetime import datetime, timedelta
from typing import Optional, Tuple, Dict, Any
from jose import JWTError, jwt, ExpiredSignatureError
from dotenv import load_dotenv
from fastapi import HTTPException, status, BackgroundTasks
from sqlalchemy.orm import Session

from app.core.background_tasks.auth_tasks import update_user_refresh_token
from app.core.cache.tokens import store_access_token, get_access_token
from app.core import logger
from app.helpers.users import get_user_by_id
from sqlalchemy.exc import SQLAlchemyError

load_dotenv()

SECRET_KEY = os.environ.get('SECRET_KEY')
ALGORITHM = os.environ.get('ALGORITHM')
ACCESS_TOKEN_EXPIRE_MINUTES = int(os.environ.get('ACCESS_TOKEN_EXPIRE_MINUTES', 30))
REFRESH_TOKEN_EXPIRE_DAYS = int(os.environ.get('REFRESH_TOKEN_EXPIRE_DAYS', 7))


def create_access_token(data: Dict[str, Any], expires_delta: Optional[timedelta] = None) -> str:
    to_encode = data.copy()
    expire = datetime.utcnow() + (expires_delta or timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES))
    to_encode.update({'exp': expire, 'type': 'access'})
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)


def create_refresh_token(data: Dict[str, Any], expires_delta: Optional[timedelta] = None) -> str:
    to_encode = data.copy()
    expire = datetime.utcnow() + (expires_delta or timedelta(days=REFRESH_TOKEN_EXPIRE_DAYS))
    to_encode.update({"exp": expire, 'type': 'refresh'})
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)


def verify_token(token: str, token_type: str) -> Dict[str, Any] | None:
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        if payload.get('type') != token_type:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid token type",
                headers={"WWW-Authenticate": "Bearer"},
            )
        return payload

    except ExpiredSignatureError:
        return None
    except JWTError:
        logger.error("Invalid Token has been sent")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )


async def get_or_create_default_tokens(db: Session, user_id: int, background_task: BackgroundTasks,
                                       register: bool = False) -> Tuple[str, str]:
    # get user from the db by id
    user = get_user_by_id(db, user_id)

    # check if the user exists
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    try:
        # get the expiry duration from the .evn
        access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
        refresh_token_expires = timedelta(days=REFRESH_TOKEN_EXPIRE_DAYS)

        # check if the user registering
        if register:
            # If registering, always create a new access token
            access_token = create_access_token(
                {"sub": str(user_id), "iat": datetime.utcnow()},
                expires_delta=access_token_expires
            )
            refresh_token = create_refresh_token(
                {"sub": str(user_id), "iat": datetime.utcnow()},
                expires_delta=refresh_token_expires
            )
            background_task.add_task(update_user_refresh_token, user_id, refresh_token)
        # if not user registering, check if the user has a valid access token in the cache or db
        else:
            # If not registering, check cache first
            access_token_from_cache = await get_access_token(user_id)

            if access_token_from_cache and verify_token(access_token_from_cache, 'access'):
                access_token = access_token_from_cache
            else:
                # Create new token if not found in cache or invalid and save new one
                access_token = create_access_token(
                    {"sub": str(user_id), "iat": datetime.utcnow()},
                    expires_delta=access_token_expires
                )
                background_task.add_task(store_access_token, access_token, user_id)
            # validate the token from db
            refresh_token_from_db = user.refresh_token
            if refresh_token_from_db and verify_token(refresh_token_from_db, 'refresh'):
                refresh_token = refresh_token_from_db
            else:
                # create new refresh token if not found in db or invalid and save it
                refresh_token = create_refresh_token(
                    {"sub": str(user_id), "iat": datetime.utcnow()},
                    expires_delta=refresh_token_expires
                )
                background_task.add_task(update_user_refresh_token, user_id, refresh_token)

        return access_token, refresh_token

    except SQLAlchemyError as db_error:
        db.rollback()
        raise HTTPException(status_code=500, detail="Database error occurred")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"An error occurred while creating tokens : {e}")
