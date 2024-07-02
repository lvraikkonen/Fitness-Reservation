from pydantic import BaseModel, EmailStr
from typing import List, Optional
from datetime import datetime


class UserBase(BaseModel):
    username: str
    email: EmailStr
    phone: str
    role: int = 0
    is_leader: bool = False
    full_name: Optional[str] = None
    department: Optional[str] = None
    preferred_sports: Optional[str] = None
    preferred_time: Optional[str] = None


class UserCreate(UserBase):
    password: str


class UserUpdate(BaseModel):
    username: Optional[str] = None
    email: Optional[str] = None
    phone: Optional[str] = None
    role: Optional[int] = None
    is_leader: Optional[bool] = None
    full_name: Optional[str] = None
    department: Optional[str] = None
    preferred_sports: Optional[str] = None
    preferred_time: Optional[str] = None


class UserResponse(UserBase):
    id: int

    class Config:
        from_attributes = True


class User(UserBase):
    id: int
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True
