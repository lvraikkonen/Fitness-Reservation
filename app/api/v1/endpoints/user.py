from fastapi import APIRouter, Depends, HTTPException, Query, UploadFile, File
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from typing import List, Optional
from datetime import date
from pathlib import Path
import uuid

from app.core.security import create_access_token
from app.core.config import settings
from app.deps import get_db
from app.models.user import User
from app.schemas.user import UserCreate, UserUpdate, UserResponse, UserDashboardResponse, \
    UpcomingReservation, RecentActivity, RecommendedVenue
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
def get_current_user_info(current_user: User = Depends(get_current_user)):
    return current_user


@router.post("/me/avatar")
async def upload_avatar(
        file: UploadFile = File(...),
        current_user: User = Depends(get_current_user),
        db: Session = Depends(get_db)
):
    user_service = UserService(db)

    # 生成唯一的文件名
    file_extension = Path(file.filename).suffix
    unique_filename = f"{uuid.uuid4()}{file_extension}"

    # 保存文件
    upload_dir = Path(settings.UPLOAD_DIRECTORY)
    file_location = upload_dir / unique_filename
    file_location.parent.mkdir(parents=True, exist_ok=True)  # 确保目录存在

    file_content = await file.read()
    file_location.write_bytes(file_content)

    # 更新用户的头像 URL
    avatar_url = f"{settings.BASE_URL}/{settings.UPLOAD_DIRECTORY}/{unique_filename}"
    user = user_service.update_user_avatar(current_user.id, avatar_url)

    return {"avatar_url": user.avatar_url}


@router.get("/dashboard", response_model=UserDashboardResponse)
def get_user_dashboard(
        user: User = Depends(get_current_user),
        db: Session = Depends(get_db)
):
    user_service = UserService(db)

    try:
        dashboard_data = user_service.get_dashboard_data(user.id)
        return dashboard_data
    except Exception as e:
        logger.error(f"Error retrieving user dashboard data: {str(e)}")
        raise HTTPException(status_code=500, detail="An error occurred while retrieving user dashboard data")


@router.get("/upcoming-reservations", response_model=List[UpcomingReservation])
def get_upcoming_reservations(
    limit: int = 3,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    user_service = UserService(db)
    return user_service.get_upcoming_reservations(current_user.id, limit)


@router.get("/recent-activities", response_model=List[RecentActivity])
def get_recent_activities(
    limit: int = 5,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    user_service = UserService(db)
    return user_service.get_recent_activities(current_user.id, limit)


@router.get("/recommended-venues", response_model=List[RecommendedVenue])
def get_recommended_venues(
    limit: int = 3,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    user_service = UserService(db)
    logger.info(f"Recommend {limit} Venues for user.")
    return user_service.get_recommended_venues(current_user, limit)


@router.get("/monthly-reservation-info", response_model=dict)
def get_monthly_reservation_info(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    user_service = UserService(db)
    count, limit = user_service.get_monthly_reservation_info(current_user.id, current_user.role)
    return {"monthly_reservation_count": count, "monthly_reservation_limit": limit}



@router.put("/me", response_model=UserResponse)
def update_current_user(user: UserUpdate, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    user_service = UserService(db)
    updated_user = user_service.update_user(current_user.id, user)
    return updated_user


@router.get("/{user_id}", response_model=UserResponse)
def get_user(user_id: int, current_user: User = Depends(get_current_admin), db: Session = Depends(get_db)):
    user_service = UserService(db)
    user = user_service.get_user(user_id)
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
