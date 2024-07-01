from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from jose import JWTError, jwt

from app.core.config import settings
from app.core.security import verify_password
from app.models.user import User
from app.schemas.token import TokenData
from app.deps import get_db
from app.services.user_service import UserService

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/v1/token")


class AuthService:
    def __init__(self, user_service: UserService = Depends()):
        self.user_service = user_service

    def authenticate_user(self, username: str, password: str) -> User:
        """
        验证用户身份
        :param username: 用户名
        :param password: 密码
        :return: 如果验证成功,返回用户对象,否则返回 None
        """
        user = self.user_service.get_user_by_username(username)
        if not user:
            return None
        if not verify_password(password, user.hashed_password):
            return None
        return user

    def get_current_user(self, token: str = Depends(oauth2_scheme)) -> User:
        """
        获取当前用户
        :param token: JWT 令牌
        :return: 当前用户对象
        :raises HTTPException: 如果验证失败,抛出 401 未授权异常
        """
        credentials_exception = HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )
        try:
            payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
            username: str = payload.get("sub")
            if username is None:
                raise credentials_exception
            token_data = TokenData(username=username)
        except JWTError:
            raise credentials_exception
        user = self.user_service.get_user_by_username(token_data.username)
        if user is None:
            raise credentials_exception
        return user

    def get_current_active_user(self, current_user: User = Depends(get_current_user)) -> User:
        """
        获取当前活跃用户
        :param current_user: 当前用户
        :return: 当前活跃用户对象
        :raises HTTPException: 如果用户不活跃,抛出 401 异常
        """
        if not current_user.is_active:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Inactive user",
                headers={"WWW-Authenticate": "Bearer"},
            )
        return current_user
