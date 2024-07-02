from pydantic import BaseModel
from typing import Optional
from app.schemas.user import User


class Token(BaseModel):
    access_token: str
    token_type: str
    user: User
