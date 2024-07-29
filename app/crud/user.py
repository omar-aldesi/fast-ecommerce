from fastapi.exceptions import HTTPException
from fastapi import BackgroundTasks, status
from sqlalchemy import and_
import uuid
from sqlalchemy.orm import Session
from app.core.cache.tokens import store_access_token
from app.core.security.tokens import get_or_create_default_tokens, verify_token, create_access_token
from app.models import User, EmailVerificationToken, ResetPasswordToken
from app.schemas.user import UserCreate, UserLogin, UserUpdate
from app.core import logger
from app.helpers.users import get_user_by_email
from app.core.background_tasks import update_last_login, update_user_refresh_token
from app.core.cache import add_refresh_token_to_blacklist, check_refresh_token
from typing import Dict
from app.core.security import validate_password
from datetime import timedelta, datetime, timezone


async def create_user(db: Session, user: UserCreate, background_task: BackgroundTasks) -> dict:
    if get_user_by_email(db, user.email):
        raise HTTPException(status_code=409, detail="Email is already registered")

    try:
        validate_password(user.password)
        db_user = User(email=user.email, first_name=user.first_name, last_name=user.last_name)
        db_user.set_password(user.password)
        db.add(db_user)
        db.flush()  # Ensure db_user.id is available before creating the token

        verification_token = EmailVerificationToken(user_id=db_user.id, token=uuid.uuid4())
        db.add(verification_token)
        db.commit()
        db.refresh(db_user)

        # TODO : add email sending func to send the uuid
        print(verification_token)
        # generate and send access / refresh tokens
        access_token, refresh_token = await get_or_create_default_tokens(db, db_user.id, background_task, register=True)

        logger.info("User registered successfully: %s", user.email)

        return {"access_token": access_token, "refresh_token": refresh_token, "token_type": "bearer"}

    except ValueError as e:
        logger.error("Invalid password: %s", str(e))
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error("Error registering user: %s", str(e))
        raise HTTPException(status_code=500, detail="Internal Server Error")


async def login_user(db: Session, credentials: UserLogin, background_task: BackgroundTasks) -> dict:
    logger.info("Logging in user: %s", credentials.email)
    # get user from email
    user = get_user_by_email(db, credentials.email)

    # check if user exists
    if not user:
        logger.info("User not found: %s", credentials.email)
        raise HTTPException(status_code=404, detail="Email or password are incorrect")

    # check user password
    if not user.check_password(credentials.password):
        logger.info("Incorrect password for user: %s", credentials.email)
        raise HTTPException(status_code=404, detail="Email or password are incorrect")

    # get or create default tokens
    logger.info("Getting or creating default tokens for user: %s", credentials.email)
    access_token, refresh_token = await get_or_create_default_tokens(db, user.id, background_task)
    background_task.add_task(update_last_login, user.id)

    logger.info("User logged in successfully: %s", credentials.email)
    return {"access_token": access_token, "refresh_token": refresh_token, "token_type": "bearer"}


async def get_refresh_token(r_token: str, background_task: BackgroundTasks) -> dict:
    # verify the token
    payload = verify_token(r_token, "refresh")

    # check the payload
    if not payload:
        logger.info("Invalid refresh token")
        raise HTTPException(status_code=401, detail="Invalid refresh token")

    # get the user id from the payload
    user_id = int(payload.get('sub'))

    # check if the refresh token are blacklisted
    if await check_refresh_token(user_id, r_token):
        raise HTTPException(status_code=401, detail="Refresh token are blacklisted.")

    # create new access token
    access_token = create_access_token({"user_id": user_id})

    # store the new access token in the cache
    background_task.add_task(store_access_token, access_token, user_id)

    logger.info("New Refresh token has been created")
    return {"access_token": access_token, "refresh_token": r_token, "token_type": "bearer"}


async def logout_user(user: User, background_task: BackgroundTasks) -> Dict[str, str]:
    r_token = user.refresh_token
    if not r_token:
        raise HTTPException(status_code=401, detail="User is not logged in")

    background_task.add_task(add_refresh_token_to_blacklist, user.id, r_token)
    background_task.add_task(update_user_refresh_token, user.id, None)
    return {"message": "User logged out successfully"}


def verify_user(db: Session, token: uuid.UUID) -> Dict[str, str]:
    try:
        db_verification = (db.query(EmailVerificationToken)
                           .filter(and_(EmailVerificationToken.token == token))
                           .first()
                           )
        if not db_verification:
            raise HTTPException(status_code=404, detail="Invalid token")

        if db_verification.created_at < datetime.now(timezone.utc) - timedelta(hours=1):
            raise HTTPException(status_code=404, detail="Expired token")

        user = db_verification.user

        if user.is_verified:
            raise HTTPException(status_code=404, detail="User already verified")

        user.is_verified = True
        db.delete(db_verification)
        db.commit()
        db.refresh(user)
        return {"message": "User verified successfully"}
    except HTTPException as e:
        raise e
    except Exception as e:
        logger.error("Error verifying user: %s", str(e))
        raise HTTPException(status_code=500, detail=f"Internal Server Error : {e}")


def send_user_verification_email(db: Session, user: User) -> Dict[str, str]:
    try:
        # get the old tokens and delete it
        old_verification_tokens = db.query(EmailVerificationToken).filter(
            and_(EmailVerificationToken.user_id == user.id))
        # check if the old tokens exists
        if old_verification_tokens:
            old_verification_tokens.delete()

        # create new token and save it in the db
        verification_token = EmailVerificationToken(
            user_id=user.id,
            token=uuid.uuid4()
        )
        db.add(verification_token)
        db.commit()
        db.refresh(verification_token)

        # send the token via email
        # TODO :  add send_email() func later
        logger.info(f"Verification email sent to {user.email}")
        return {"message": "Verification email sent successfully"}
    except Exception as e:
        logger.error("Error sending verification email: %s", str(e))
        raise HTTPException(status_code=500, detail="Internal Server Error")


def change_user_password(db: Session, user: User, new_password: str, old_password: str) -> Dict[str, str]:
    try:
        if not user.check_password(old_password):
            raise HTTPException(status_code=400, detail="Old Password are incorrect")
        if user.check_password(new_password):
            raise HTTPException(status_code=400, detail="New password cannot be the same as the old password")
        validate_password(new_password)
        user.set_password(new_password)
        db.commit()
        db.refresh(user)
        return {"message": "Password changed successfully"}
    except ValueError as e:
        logger.error("Invalid password: %s", str(e))
        raise HTTPException(status_code=400, detail=str(e))
    except HTTPException as e:
        raise e
    except Exception as e:
        logger.error("Error changing password: %s", str(e))
        raise HTTPException(status_code=500, detail="Internal Server Error")


def reset_user_password_request(db: Session, user: User):
    try:
        old_reset_password_tokens = db.query(ResetPasswordToken).filter(
            and_(ResetPasswordToken.user_id == user.id))
        if old_reset_password_tokens:
            old_reset_password_tokens.delete()

        reset_token = ResetPasswordToken(
            user_id=user.id,
        )
        db.add(reset_token)
        db.commit()
        db.refresh(reset_token)
        # TODO : add send_email() func
        return {"message": "Reset password email sent successfully"}
    except HTTPException as e:
        raise e
    except Exception as e:
        logger.error("Error resetting password: %s", str(e))
        raise HTTPException(status_code=500, detail="Internal Server Error")


def reset_user_password_confirm(db: Session, token: uuid.UUID, new_password: str):
    try:
        validate_password(new_password)
        db_reset_token = db.query(ResetPasswordToken).filter(
            and_(ResetPasswordToken.token == token)).first()
        if not db_reset_token:
            raise HTTPException(status_code=404, detail="Invalid token")
        if db_reset_token.created_at < datetime.now(timezone.utc) - timedelta(hours=1):
            raise HTTPException(status_code=404, detail="Expired token")
        user = db_reset_token.user
        user.set_password(new_password)
        db.delete(db_reset_token)
        db.commit()
        db.refresh(user)
        return {"message": "Password reset successfully"}
    except HTTPException as e:
        raise e
    except ValueError as e:
        logger.error("Invalid password: %s", str(e))
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error("Error resetting password: %s", str(e))
        raise HTTPException(status_code=500, detail="Internal Server Error")


def user_update(db: Session, user: User, fields: UserUpdate):
    try:
        update_data = fields.model_dump(exclude_unset=True)
        if not update_data:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,
                                detail="No valid fields to update")
        if 'email' in update_data:
            if get_user_by_email(db, update_data['email']):
                raise HTTPException(status_code=status.HTTP_409_CONFLICT,
                                    detail="Email is already registered")

        if 'phone_number' in update_data:
            if db.query(User).filter(User.phone_number == update_data['phone_number']).first():
                raise HTTPException(status_code=status.HTTP_409_CONFLICT,
                                    detail="Phone number is already registered")

        for key, value in update_data.items():
            setattr(user, key, value)

        db.add(user)
        db.commit()
        db.refresh(user)
        return {"message": "User updated successfully"}
    except HTTPException as e:
        raise e
    except Exception as e:
        logger.error("Error updating user: %s", str(e))
        raise HTTPException(status_code=500, detail="Internal Server Error")
