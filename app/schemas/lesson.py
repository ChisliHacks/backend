from pydantic import BaseModel
from datetime import datetime
from typing import Optional


class LessonBase(BaseModel):
    title: str
    description: Optional[str] = None
    category: str
    filename: Optional[str] = None
    duration_minutes: Optional[int] = None
    difficulty_level: Optional[str] = "beginner"
    is_published: Optional[bool] = False


class LessonCreate(LessonBase):
    instructor_id: Optional[int] = None


class LessonUpdate(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    category: Optional[str] = None
    filename: Optional[str] = None
    duration_minutes: Optional[int] = None
    difficulty_level: Optional[str] = None
    is_published: Optional[bool] = None
    instructor_id: Optional[int] = None


class LessonResponse(LessonBase):
    id: int
    instructor_id: Optional[int] = None
    created_at: datetime
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True


class LessonListResponse(BaseModel):
    id: int
    title: str
    description: Optional[str] = None
    category: str
    filename: Optional[str] = None
    duration_minutes: Optional[int] = None
    difficulty_level: str
    is_published: bool
    created_at: datetime

    class Config:
        from_attributes = True
