from datetime import datetime, timedelta
from typing import Optional, Union
from jose import JWTError, jwt
from passlib.context import CryptContext
from app.core.config import settings

# 定义密码哈希上下文
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """
    验证明文密码和哈希密码是否匹配
    :param plain_password: 明文密码
    :param hashed_password: 哈希密码
    :return: 如果匹配，返回 True，否则返回 False
    """
    return pwd_context.verify(plain_password, hashed_password)


def get_password_hash(password: str) -> str:
    """
    生成密码的哈希值
    :param password: 明文密码
    :return: 哈希后的密码
    """
    return pwd_context.hash(password)


def create_access_token(data: dict, expires_delta: Optional[timedelta] = None) -> str:
    """
    生成 JWT 访问令牌
    :param data: 要编码到 JWT 中的数据
    :param expires_delta: 令牌的过期时间，如果未提供，则使用默认过期时间
    :return: 编码后的 JWT 令牌
    """
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM)
    return encoded_jwt


def decode_access_token(token: str) -> Union[dict, None]:
    """
    解码 JWT 访问令牌
    :param token: 要解码的 JWT 令牌
    :return: 令牌的负载数据，如果解码失败，返回 None
    """
    try:
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
        return payload
    except JWTError:
        return None


def create_password_reset_token(user_id: int) -> str:
    expire = datetime.utcnow() + timedelta(hours=24)
    to_encode = {
        "exp": expire,
        "user_id": user_id,
        "type": "password_reset"
    }
    return jwt.encode(to_encode, settings.SECRET_KEY, algorithm="HS256")


def verify_password_reset_token(token: str) -> Optional[int]:
    try:
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=["HS256"])
        if payload["type"] != "password_reset":
            return None
        user_id = payload["user_id"]
        return user_id
    except jwt.JWTError:
        return None
