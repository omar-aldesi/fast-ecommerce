from fastapi import Depends, APIRouter, BackgroundTasks, HTTPException, Request
from starlette import status
from sqlalchemy.orm import Session
from app.db.session import get_db
from app.schemas.user import UserCreate, UserLogin, UserChangePassword, UserPasswordReset, UserUpdate, UserProfile
from app.schemas.token import Token, RefreshToken
from app.crud.user import create_user, login_user, get_refresh_token, logout_user, verify_user, change_user_password, \
    send_user_verification_email, reset_user_password_confirm, reset_user_password_request, user_update

from app.models import User
from app.core.deps import get_current_user
import uuid

router = APIRouter()


@router.post('/register', response_model=Token, status_code=status.HTTP_201_CREATED)
async def register(user: UserCreate, background_task: BackgroundTasks, db: Session = Depends(get_db)):
    return await create_user(db, user, background_task)


@router.post('/login', response_model=Token)
async def login(credentials: UserLogin, background_task: BackgroundTasks, db: Session = Depends(get_db)):
    return await login_user(db, credentials, background_task)


@router.post("/token/refresh", response_model=Token, status_code=status.HTTP_201_CREATED)
async def refresh(request: RefreshToken, background_task: BackgroundTasks):
    return await get_refresh_token(request.refresh_token, background_task)


@router.post('/logout')
async def logout(background_task: BackgroundTasks, user: User = Depends(get_current_user)) -> dict[str, str]:
    return await logout_user(user, background_task)


@router.get('/verify/{token}')
def verify(token: uuid.UUID, db: Session = Depends(get_db)):
    return verify_user(db, token)


@router.post('/resend-verification-token')
def resend_verification_token(user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    if user.is_verified:
        raise HTTPException(status_code=400, detail="User already verified")
    return send_user_verification_email(db, user)


@router.post('/change-password')
def change_password(request: UserChangePassword, db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    return change_user_password(db, user, request.new_password, request.old_password)


@router.post('/reset-password/request')
def reset_password_request(db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    return reset_user_password_request(db, user)


@router.post('/reset-password/confirm')
def reset_password_confirm(request: UserPasswordReset, db: Session = Depends(get_db)):
    return reset_user_password_confirm(db, request.token, request.new_password)


@router.patch('/update-user')
def update_user(request: UserUpdate, db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    return user_update(db, user, request)


@router.get('/profile', response_model=UserProfile)
def user_profile(user: User = Depends(get_current_user)):
    return user
