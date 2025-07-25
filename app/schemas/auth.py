from pydantic import BaseModel, EmailStr
from typing import Optional


class UserRegister(BaseModel):
    email: EmailStr
    username: str
    password: str


class UserLogin(BaseModel):
    username: str
    password: str


class Token(BaseModel):
    access_token: str
    token_type: str


class TokenData(BaseModel):
    username: Optional[str] = None


class UserProfile(BaseModel):
    id: int
    email: EmailStr
    username: str
    is_active: bool
    lessons_completed: int
    total_lesson_score: int

    class Config:
        from_attributes = True
