from sqlalchemy.orm import Session
from typing import List
from fastapi import Depends, HTTPException

from app.models.user import User
from app.schemas.user import UserCreate, UserUpdate, UserResponse
from app.core.security import (get_password_hash, verify_password,
                               create_password_reset_token, verify_password_reset_token)
from app.deps import get_db
# from app.services.log_services import log_operation
from app.core.config import settings, get_logger
from app.utils.email import send_reset_password_email

logger = get_logger(__name__)


class UserService:
    def __init__(self, db: Session = Depends(get_db)):
        self.db = db

    def get_user_by_id(self, user_id: int) -> User:
        user = self.db.query(User).filter(User.id == user_id).first()
        if not user:
            raise HTTPException(status_code=404, detail="User not found")
        return user

    def get_user_by_username(self, username: str) -> User:
        user = self.db.query(User).filter(User.username == username).first()
        if not user:
            raise HTTPException(status_code=404, detail="User not found")
        return user

    def get_users(self, skip: int = 0, limit: int = 100) -> List[User]:
        return self.db.query(User).offset(skip).limit(limit).all()

    def create_user(self, user: UserCreate) -> UserResponse:
        existing_user = self.db.query(User).filter(
            (User.username == user.username) | (User.email == user.email)
        ).first()
        if existing_user:
            raise HTTPException(
                status_code=400,
                detail="Username or email already registered!"
            )
        # new create user
        hashed_password = get_password_hash(user.password)
        db_user = User(
            username=user.username,
            email=user.email,
            password=hashed_password,
            phone=user.phone,
            role=user.role,
            is_leader=user.is_leader,
            full_name=user.full_name,
            department=user.department,
            preferred_sports=user.preferred_sports,
            preferred_time=user.preferred_time
        )
        self.db.add(db_user)
        self.db.commit()
        self.db.refresh(db_user)
        # log_operation(db_user.id, "register", {"username": db_user.username})
        return UserResponse.from_orm(db_user)

    def update_user(self, user_id: int, user: UserUpdate) -> User:
        db_user = self.get_user_by_id(user_id)
        update_data = user.dict(exclude_unset=True)
        for key, value in update_data.items():
            setattr(db_user, key, value)
        self.db.commit()
        self.db.refresh(db_user)
        return db_user

    def authenticate_user(self, username: str, password: str) -> User:
        user = self.get_user_by_username(username)
        if not user:
            raise HTTPException(status_code=404, detail="User doesn't exists.")
        if not verify_password(password, user.password):
            raise HTTPException(
                status_code=401,
                detail="Incorrect username or password"
            )
        logger.info(f"User: {user.username} has just login. UserId: {user.id}")
        return user

    def delete_user(self, user_id: int):
        db_user = self.get_user_by_id(user_id)
        self.db.delete(db_user)
        self.db.commit()

    def request_password_reset(self, email: str) -> bool:
        user = self.db.query(User).filter(User.email == email).first()
        if not user:
            return False

        token = create_password_reset_token(user.id)
        reset_link = f"{settings.FRONTEND_BASE_URL}/reset-password?token={token}"
        print(reset_link)
        send_reset_password_email(user.email, user.username, reset_link)

        return True

    def reset_password(self, token: str, new_password: str) -> bool:
        user_id = verify_password_reset_token(token)
        if not user_id:
            return False

        user = self.db.query(User).filter(User.id == user_id).first()
        if not user:
            return False

        user.password = get_password_hash(new_password)
        self.db.commit()

        return True
