from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError
from typing import List, Optional
from fastapi import Depends

from app.models.user import User
from app.schemas.user import UserCreate, UserUpdate, UserResponse
from app.core.security import (get_password_hash, verify_password,
                               create_password_reset_token, verify_password_reset_token)
from app.deps import get_db
# from app.services.log_services import log_operation
from app.core.config import settings, get_logger
from app.utils.email import send_email_async
from app.utils.templates import get_notification_template
from app.core.exceptions import UserNotFoundError, UserAlreadyExistsError, ValidationError, AuthenticationError

logger = get_logger(__name__)


class UserService:
    def __init__(self, db: Session = Depends(get_db)):
        self.db = db

    def get_user(self, user_id: Optional[int] = None, username: Optional[str] = None, email: Optional[str] = None) -> User:
        if user_id:
            user = self.db.query(User).filter(User.id == user_id).first()
        elif username:
            user = self.db.query(User).filter(User.username == username).first()
        elif email:
            user = self.db.query(User).filter(User.email == email).first()
        else:
            raise ValueError("Either user_id, username or email must be provided")

        if not user:
            raise UserNotFoundError("User not found")
        return user

    def get_users(self, skip: int = 0, limit: int = 100) -> List[User]:
        return self.db.query(User).offset(skip).limit(limit).all()

    def create_user(self, user: UserCreate) -> UserResponse:
        try:
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
            logger.info(f"New user created: {db_user.username}")
            return UserResponse.from_orm(db_user)
        except IntegrityError:
            self.db.rollback()
            logger.warning(f"Attempt to create duplicate user: {user.username}")
            raise UserAlreadyExistsError("Username or email already registered!")

    def update_user(self, user_id: int, user: UserUpdate) -> User:
        db_user = self.get_user(user_id=user_id)
        update_data = user.dict(exclude_unset=True)

        # Check if email is being updated and if it's already in use
        if 'email' in update_data:
            existing_user = self.db.query(User).filter(User.email == update_data['email']).first()
            if existing_user and existing_user.id != user_id:
                raise UserAlreadyExistsError("Email already in use")

        for key, value in update_data.items():
            setattr(db_user, key, value)

        try:
            self.db.commit()
            self.db.refresh(db_user)
            logger.info(f"User updated: {db_user.username}")
            return db_user
        except IntegrityError:
            self.db.rollback()
            logger.warning(f"Failed to update user: {db_user.username}")
            raise ValidationError("Failed to update user")

    def authenticate_user(self, username: str, password: str) -> User:
        try:
            user = self.get_user(username=username)
            if not verify_password(password, user.password):
                raise AuthenticationError("Incorrect username or password")
            logger.info(f"User authenticated: {user.username}")
            return user
        except UserNotFoundError:
            raise AuthenticationError("Incorrect username or password")

    def delete_user(self, user_id: int):
        db_user = self.get_user(user_id=user_id)
        self.db.delete(db_user)
        self.db.commit()
        logger.info(f"User deleted: {db_user.username}")

    def get_user_by_email(self, email: str) -> User:
        user = self.db.query(User).filter(User.email == email).first()
        if not user:
            raise UserNotFoundError(f"User with email {email} not found")
        return user

    def create_password_reset_token(self, user_id: int) -> str:
        token = create_password_reset_token(user_id)
        reset_link = f"{settings.FRONTEND_BASE_URL}/reset-password?token={token}"
        return reset_link

    async def send_password_reset_email(self, user: User, reset_link: str) -> bool:
        subject = "Password Reset Request"
        body = get_notification_template("reset_password", {
            "username": user.username,
            "reset_link": reset_link
        })

        try:
            await send_email_async(user.email, subject, body)
            logger.info(f"Password reset email sent to: {user.email}")
            return True
        except Exception as e:
            logger.error(f"Failed to send password reset email to {user.email}: {str(e)}")
            return False

    async def request_password_reset(self, email: str) -> bool:
        try:
            user = self.get_user_by_email(email)
            reset_link = self.create_password_reset_token(user.id)
            success = await self.send_password_reset_email(user, reset_link)
            if success:
                logger.info(f"Password reset requested for user: {user.username}")
            return success
        except UserNotFoundError:
            logger.warning(f"Password reset requested for non-existent email: {email}")
            return False

    def reset_password(self, token: str, new_password: str) -> bool:
        user_id = verify_password_reset_token(token)
        if not user_id:
            logger.warning("Invalid password reset token")
            return False

        try:
            user = self.get_user(user_id=user_id)
            user.password = get_password_hash(new_password)
            self.db.commit()
            logger.info(f"Password reset successful for user: {user.username}")
            return True
        except UserNotFoundError:
            logger.warning(f"Password reset failed for non-existent user ID: {user_id}")
            return False

    def check_rate_limit(self, user_id: int, action: str) -> None:
        # Implement rate limiting logic here
        # For example, check the number of actions performed by the user in the last hour
        # If it exceeds a certain threshold, raise RateLimitExceededError
        pass
