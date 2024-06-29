from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from jose import JWTError, jwt
from app.core.config import settings
from sqlalchemy.orm import Session
from app.core.security import verify_password, decode_access_token
from app.models.user import User
from app.schemas.user import TokenData
from app.db.database import get_db
from app.services.user_service import get_user_by_name

# 定义 OAuth2 密码流，用于获取访问令牌
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/v1/token")


def authenticate_user(db: Session, username: str, password: str):
    """
    验证用户身份
    :param db: 数据库会话
    :param username: 用户名
    :param password: 密码
    :return: 如果验证成功，返回用户对象，否则返回 False
    """
    user = get_user_by_name(db, username)
    if not user:
        return False
    if not verify_password(password, user.hashed_password):
        return False
    return user


def get_current_user(token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)):
    """
    获取当前用户
    :param token: JWT 令牌
    :param db: 数据库会话
    :return: 当前用户对象
    :raises HTTPException: 如果验证失败，抛出 401 未授权异常
    """
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = decode_access_token(token)
        username: str = payload.get("sub")
        if username is None:
            raise credentials_exception
        token_data = TokenData(username=username)
    except JWTError:
        raise credentials_exception
    user = get_user_by_name(db, token_data.username)
    if user is None:
        raise credentials_exception
    return user


def get_current_active_user(current_user: User = Depends(get_current_user)):
    """
    获取当前活跃用户
    :param current_user: 当前用户
    :return: 当前活跃用户对象
    :raises HTTPException: 如果用户不活跃，抛出 400 异常
    """
    if not current_user.is_active:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Inactive user",
            headers={"WWW-Authenticate": "Bearer"},
        )
    return current_user
