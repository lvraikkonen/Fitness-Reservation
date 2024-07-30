from fastapi import APIRouter, Depends, HTTPException, Query
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from typing import List, Optional
from datetime import date

from app.core.security import create_access_token
from app.deps import get_db
from app.models.user import User
from app.schemas.user import UserCreate, UserUpdate, UserResponse
from app.schemas.token import Token
from app.schemas.reservation import PaginatedReservationResponse
from app.schemas.user import UserResetPasswordRequest, UserResetPassword
from app.services.user_service import UserService
from app.deps import get_current_user, get_current_admin
from app.core.config import get_logger
from app.core.exceptions import AuthorizationError

router = APIRouter()
logger = get_logger(__name__)


@router.post("/register", response_model=UserResponse, status_code=201)
def register_user(user: UserCreate, db: Session = Depends(get_db)):
    return UserService(db).create_user(user)


@router.post("/login", response_model=Token)
def login_user(form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    try:
        user_service = UserService(db)
        user = user_service.authenticate_user(form_data.username, form_data.password)
        if not user:
            raise HTTPException(status_code=401, detail="Invalid username or password")
        access_token = create_access_token({"sub": user.username})
    except ValueError as e:
        raise HTTPException(status_code=422, detail=str(e))
    return {"access_token": access_token, "token_type": "bearer", "user": user}


@router.get("/me", response_model=UserResponse)
def get_current_user(current_user: User = Depends(get_current_user)):
    return current_user


@router.put("/me", response_model=UserResponse)
def update_current_user(user: UserUpdate, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    user_service = UserService(db)
    updated_user = user_service.update_user(current_user.id, user)
    return updated_user


@router.get("/{user_id}", response_model=UserResponse)
def get_user(user_id: int, current_user: User = Depends(get_current_admin), db: Session = Depends(get_db)):
    user_service = UserService(db)
    user = user_service.get_user_by_id(user_id)
    return user


@router.get("/", response_model=List[UserResponse])
def get_users(skip: int = 0, limit: int = 100, current_user: User = Depends(get_current_admin), db: Session = Depends(get_db)):
    users = UserService(db).get_users(skip, limit)
    return [UserResponse.from_orm(user) for user in users]


@router.put("/{user_id}", response_model=UserResponse)
def update_user(user_id: int, user: UserUpdate, current_user: User = Depends(get_current_admin), db: Session = Depends(get_db)):
    user_service = UserService(db)
    updated_user = user_service.update_user(user_id, user)
    return updated_user


@router.delete("/{user_id}")
def delete_user(user_id: int, current_user: User = Depends(get_current_admin), db: Session = Depends(get_db)):
    user_service = UserService(db)
    user_service.delete_user(user_id)
    return {"message": "User deleted successfully"}


@router.post("/reset-password-request", response_model=dict)
def reset_password_request(
    reset_request: UserResetPasswordRequest,
    db: Session = Depends(get_db)
):
    user_service = UserService(db)
    success = user_service.request_password_reset(reset_request.email)
    if not success:
        raise HTTPException(status_code=404, detail="User not found")
    return {"message": "Password reset email sent successfully"}


@router.post("/reset-password", response_model=dict)
def reset_password(
    reset_data: UserResetPassword,
    db: Session = Depends(get_db)
):
    user_service = UserService(db)
    success = user_service.reset_password(reset_data.token, reset_data.new_password)
    if not success:
        raise HTTPException(status_code=400, detail="Invalid or expired token")
    return {"message": "Password reset successfully"}


@router.get("/users/{user_id}/reservation-history", response_model=PaginatedReservationResponse)
def get_user_reservation_history(
        user_id: int,
        start_date: Optional[date] = None,
        end_date: Optional[date] = None,
        page: int = Query(1, ge=1),
        page_size: int = Query(20, ge=1, le=100),
        current_user: User = Depends(get_current_user),
        db: Session = Depends(get_db)
):
    user_service = UserService(db)

    # 检查权限：只允许用户查看自己的历史记录，或者管理员可以查看所有用户的历史记录
    if current_user.id != user_id and not current_user.is_admin:
        raise AuthorizationError("Not authorized to view this user's history")

    try:
        return user_service.get_user_reservation_history(user_id, start_date, end_date, page, page_size)
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        logger.error(f"Error retrieving user reservation history: {str(e)}")
        raise HTTPException(status_code=500, detail="An error occurred while retrieving reservation history")
